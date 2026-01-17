
from datetime import datetime, timedelta, timezone
import psycopg2
import os
from google.cloud import bigquery
from app.core.config import settings
import ccxt as ccxt_sync
import logging
import statistics
import redis
import json

# Define logger
logger = logging.getLogger("MarketDataProvider")

class MarketDataProvider:
    """
    Unified Data Provider (Singleton).
    Routes requests to Hot (SQL) and Cold (BQ) storage.
    Fills gaps via Linear Interpolation (Emergency Mode).
    Appends LIVE Candle from Redis.
    Guards Data Integrity (No Zeroes, No Spikes).
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MarketDataProvider, cls).__new__(cls)
            
            # BigQuery Client (Cold Storage)
            try:
                cls._instance.bq_client = bigquery.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))
            except Exception as e:
                logger.warning(f"⚠️ BigQuery Init Failed: {e}")
                cls._instance.bq_client = None

            # 2. Exchange (CCXT)
            try:
                cls._instance.exchange = ccxt_sync.binance()
                cls._instance.exchange_fallback = ccxt_sync.kucoin() # Fallback
            except Exception as e:
                logger.error(f"❌ CCXT Init Failed: {e}")
                cls._instance.exchange = None
                cls._instance.exchange_fallback = None

            # 3. Redis (Safe Init)
            try:
                cls._instance.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
                # Test connection
                cls._instance.redis.ping()
            except Exception as e:
                logger.warning(f"⚠️ Redis Init Failed: {e}")
                cls._instance.redis = None
        return cls._instance

    def get_continuous_history(self, symbol: str, start_date: datetime, end_date: datetime, timeframe: str = '4h'):
        """
        Fetch continuous history.
        Safety Mode: Force SQL only for 1h/4h to avoid BQ contamination.
        Append Live Candle.
        """
        # 1. Fetch from Hot Storage (Cloud SQL)
        hot_data = self._fetch_sql(symbol, start_date, end_date, timeframe)
        
        # 2. Safety Check: Only use BigQuery if timeframe is > 4h (e.g. 1d) or explicitly allowed
        cold_data = []
        if timeframe not in ['1h', '4h']:
             cold_data = self._fetch_bq(symbol, start_date, end_date, timeframe)
        
        # 3. Merge & Deduplicate
        combined = {d['time']: d for d in cold_data}
        for d in hot_data:
            combined[d['time']] = d # Hot overrides Cold
            
        sorted_data = sorted(combined.values(), key=lambda x: x['time'])

        # FILTER ZERO PRICES
        sorted_data = [d for d in sorted_data if d['close'] > 0 and d['high'] > 0 and d['low'] > 0 and d['open'] > 0]
        
        if not sorted_data:
            # ON-DEMAND FAILOVER (The "Immediate Fix")
            # If DB is empty, fetch from Exchange NOW.
            logger.warning(f"⚠️ No data in DB for {symbol} {timeframe}. Fetching from Exchange...")
            try:
                # Convert timeframe if needed (standardize)
                tf_map = {'1m':'1m','5m':'5m','15m':'15m','30m':'30m','1h':'1h','4h':'4h','1d':'1d','1w':'1w'}
                exch_tf = tf_map.get(timeframe, timeframe)
                
                # Calculate 'since' timestamp based on start_date
                since_ts = int(start_date.timestamp() * 1000)
                
                # Fetch (limit 1000 to cover safe range)
                candles = []
                try:
                    candles = self.exchange.fetch_ohlcv(symbol, exch_tf, since=since_ts, limit=1000)
                except Exception as b_err:
                    logger.warning(f"⚠️ Binance Fetch Failed ({b_err}). Trying Fallback...")
                    if self.exchange_fallback:
                        try:
                            # KuCoin might use different symbol format? CCXT usually normalizes.
                            # Try Standard
                            candles = self.exchange_fallback.fetch_ohlcv(symbol, exch_tf, since=since_ts, limit=1000)
                            logger.info(f"✅ Fallback (KuCoin) fetch successful.")
                        except Exception as k_err:
                             logger.error(f"❌ Fallback also failed: {k_err}")
                
                if candles:
                    logger.info(f"✅ On-Demand fetch successful: {len(candles)} candles")
                    
                    # Convert to internal format
                    sorted_data = []
                    conn = psycopg2.connect(settings.DATABASE_URL)
                    cursor = conn.cursor()
                    
                    for c in candles:
                        c_dt = datetime.fromtimestamp(c[0]/1000, tz=timezone.utc)
                        row = {
                            "time": c_dt.isoformat(),
                            "open": float(c[1]),
                            "high": float(c[2]),
                            "low": float(c[3]),
                            "close": float(c[4]),
                            "volume": float(c[5])
                        }
                        sorted_data.append(row)
                        
                        # Persist to DB for next time (Write-Through)
                        cursor.execute("""
                            INSERT INTO ohlcv (time, symbol, timeframe, open, high, low, close, volume)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (time, symbol, timeframe) DO NOTHING
                        """, (c_dt, symbol, timeframe, row['open'], row['high'], row['low'], row['close'], row['volume']))
                        
                    conn.commit()
                    cursor.close()
                    conn.close()
                else:
                    return []
            except Exception as e:
                logger.error(f"❌ On-Demand Fetch Logic Failed: {e}")
                return []

        # 4. Anomaly Detection & Cleaning
        cleaned_data = self._clean_anomalies(symbol, sorted_data, timeframe)
        
        # 5. Gap Filling (Linear Interpolation)
        filled_data = self._fill_gaps_interp(cleaned_data, timeframe)
        
        # 5b. BRIDGE REALTIME GAP (The Bridge)
        bridged_data = self._bridge_realtime_gap(symbol, filled_data, timeframe)
        
        # 6. Append LIVE Candle (Real-Time Builder)
        final_data = self._append_live_candle(symbol, bridged_data, timeframe)
        
        # 7. VALIDATOR & AUTO-REPAIR
        self._validate_and_repair(symbol, final_data, timeframe)
        
        return final_data

    def _validate_and_repair(self, symbol: str, data: list, timeframe: str):
        """
        Ensures perfect continuity. If a gap is found:
        1. Fetches specific missing range from Exchange.
        2. Saves to DB.
        3. Raises 503 to force Client Refresh (which will load the fixed data).
        """
        if not data or len(data) < 2: return
        
        # Parse tf delta
        tf_delta = timedelta(hours=1)
        if timeframe == '4h': tf_delta = timedelta(hours=4)
        elif timeframe == '1d': tf_delta = timedelta(days=1)
        elif timeframe == '1m': tf_delta = timedelta(minutes=1)
        
        repaired_any = False
        
        for i in range(len(data) - 1):
             curr_time = datetime.fromisoformat(data[i]['time'])
             next_time = datetime.fromisoformat(data[i+1]['time'])
             
             # Check gap
             diff = next_time - curr_time
             # Tolerance 1.1x (allow small drift, but 1h must be 1h)
             if diff > tf_delta * 1.1:
                 missing_ts = curr_time + tf_delta
                 logger.error(f"❌ DATA INCONSISTENCY: Missing {missing_ts}. Triggering Emergency Repair.")
                 
                 try:
                     # Emergency Fetch
                     since_ts = int(missing_ts.timestamp() * 1000)
                     candles = self.exchange.fetch_ohlcv(symbol, timeframe, since=since_ts, limit=5) # Fetch small batch
                     
                     if candles:
                         conn = psycopg2.connect(settings.DATABASE_URL)
                         cursor = conn.cursor()
                         
                         for c in candles:
                             c_dt = datetime.fromtimestamp(c[0]/1000, tz=timezone.utc)
                             
                             # Validate it plugs the gap
                             if c_dt >= next_time: break 
                             
                             cursor.execute("""
                                INSERT INTO ohlcv (time, symbol, timeframe, open, high, low, close, volume)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (time, symbol, timeframe) DO UPDATE SET close = EXCLUDED.close
                             """, (c_dt, symbol, timeframe, c[1], c[2], c[3], c[4], c[5]))
                             
                         conn.commit()
                         cursor.close()
                         conn.close()
                         repaired_any = True
                 except Exception as e:
                     logger.error(f"Emergency repair failed: {e}")

        if repaired_any:
            # Force refresh to load new data
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail="Data Gap Detected - System Repairing... Please Refresh.")

    def _bridge_realtime_gap(self, symbol: str, data: list, timeframe: str):
        """
        Fetches missing candles from Exchange if there is a gap between 
        DB history and NOW. This prevents the 'floating candle' issue.
        """
        if not data: return data
        
        last_candle_time = datetime.fromisoformat(data[-1]['time'])
        now = datetime.now(timezone.utc)
        
        # Determine timeframe delta
        tf_delta = timedelta(hours=1)
        if timeframe == '4h': tf_delta = timedelta(hours=4)
        elif timeframe == '1d': tf_delta = timedelta(days=1)
        elif timeframe == '1m': tf_delta = timedelta(minutes=1) # added support
        
        # If gap is larger than 2 candles, we need to bridge
        if (now - last_candle_time) > tf_delta * 1.5:
            logger.warning(f"⚠️ Bridging Gap detected: {now - last_candle_time}. Fetching from Exchange...")
            try:
                # Fetch since last candle + 1 tf
                since_ts = int((last_candle_time + tf_delta).timestamp() * 1000)
                
                # Native 2026 Fetch
                candles = self.exchange.fetch_ohlcv(symbol, timeframe, since=since_ts, limit=50)
                
                if candles:
                    logger.success(f"✅ Bridge constructed with {len(candles)} candles.")
                    
                    # PERSIST BRIDGE TO DB
                    try:
                         conn = psycopg2.connect(settings.DATABASE_URL)
                         cursor = conn.cursor()
                         
                         for c in candles:
                             c_dt = datetime.fromtimestamp(c[0]/1000, tz=timezone.utc)
                             
                             # Add to list
                             data.append({
                                 "time": c_dt.isoformat(),
                                 "open": c[1],
                                 "high": c[2],
                                 "low": c[3],
                                 "close": c[4],
                                 "volume": c[5]
                             })
                             
                             # Save to DB
                             cursor.execute("""
                                INSERT INTO ohlcv (time, symbol, timeframe, open, high, low, close, volume)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (time, symbol, timeframe) DO NOTHING
                             """, (c_dt, symbol, timeframe, c[1], c[2], c[3], c[4], c[5]))
                             
                         conn.commit()
                         cursor.close()
                         conn.close()
                         
                    except Exception as db_e:
                        logger.error(f"Failed to persist bridge: {db_e}")
                        
            except Exception as e:
                logger.error(f"Bridge Construction Failed: {e}")
                
        return data

    def _append_live_candle(self, symbol: str, data: list, timeframe: str):
        """Builds and appends the current forming candle from Redis ticker"""
        if not self.redis or not data:
            return data
            
        try:
            # Get latest ticker
            ticker_json = self.redis.get(f"ticker:{symbol.replace('/', '')}")
            if not ticker_json:
                return data
                
            ticker = json.loads(ticker_json)
            last_price = float(ticker['last'])
            ts_ms = float(ticker['timestamp'])
            
            # Determine candle start time
            tf_seconds = 3600 # default 1h
            if timeframe == '4h': tf_seconds = 14400
            elif timeframe == '1d': tf_seconds = 86400
            elif timeframe == '1m': tf_seconds = 60
            
            ts_seconds = ts_ms / 1000.0
            candle_start_ts = ts_seconds - (ts_seconds % tf_seconds)
            candle_time_str = datetime.fromtimestamp(candle_start_ts, tz=timezone.utc).isoformat()
            
            # Check if last stored candle is this current candle
            if not data:
                 return data # Should not happen if history exists
                 
            last_candle = data[-1]
            last_candle_ts = datetime.fromisoformat(last_candle['time']).timestamp()
            
            # Tolerance for float comparison
            if abs(last_candle_ts - candle_start_ts) < 1.0:
                # Update existing last candle with live price
                # We trust DB open/high/low more than single tick, but update Close
                if last_price > last_candle['high']: last_candle['high'] = last_price
                if last_price < last_candle['low']: last_candle['low'] = last_price
                last_candle['close'] = last_price
            elif candle_start_ts > last_candle_ts:
                # Append NEW candle
                # Use close of previous as open (smoothness)
                prev_close = last_candle['close']
                data.append({
                    "time": candle_time_str,
                    "open": prev_close, # Smoothed Open
                    "high": max(prev_close, last_price),
                    "low": min(prev_close, last_price),
                    "close": last_price,
                    "volume": 0 
                })
        except Exception as e:
            logger.warning(f"Live Candle Error: {e}")
            
        return data

    def _clean_anomalies(self, symbol, data, timeframe):
        """
        Filter out records where price deviates > 50% from 24h Mean.
        Attempt to repair via CCXT.
        """
        if len(data) < 24: return data
        
        valid_data = []
        
        for i in range(len(data)):
             current = data[i]
             if i < 24:
                 valid_data.append(current)
                 continue
             
             # Calculate MA of LAST 24 valid records
             window = [p['close'] for p in valid_data[-24:]]
             if not window:
                 valid_data.append(current)
                 continue
                 
             ma = sum(window) / len(window)
             deviation = abs(current['close'] - ma) / ma
             
             if deviation > 0.50: # 50% tolerance (Spike Guard)
                 logger.warning(f"⚠️ ANOMALY DETECTED: {current['time']} Price {current['close']} vs MA {ma:.2f}. Attempting repair...")
                 
                 # REPAIR via CCXT
                 try:
                     # Fetch SINGLE candle
                     bad_dt = datetime.fromisoformat(current['time'])
                     fetch_ts = int(bad_dt.timestamp() * 1000) # Native 2026 (No Shift)
                     
                     candles = self.exchange.fetch_ohlcv(symbol, timeframe, since=fetch_ts, limit=1)
                     if candles:
                         c = candles[0]
                         current['open'] = c[1]
                         current['high'] = c[2]
                         current['low'] = c[3]
                         current['close'] = c[4]
                         current['volume'] = c[5]
                         logger.success(f"✅ REPAIRED {current['time']} with price {current['close']}")
                     else:
                         # Interpolate if fetch fails
                         prev = valid_data[-1]
                         current['open'] = prev['close']
                         current['close'] = prev['close']
                         current['high'] = prev['close']
                         current['low'] = prev['close']
                         logger.warning("Repair failed, interpolated.")
                 except Exception as e:
                     logger.error(f"Repair Error: {e}")
                     # Drop if cant repair
                     continue 
             
             valid_data.append(current)
             
        return valid_data

    def _fill_gaps_interp(self, data, timeframe):
        """
        Fill missing candles using Linear Interpolation.
        """
        if not data: return []
        
        # Parse timeframe to timedelta
        tf_delta = None
        if timeframe == '1h': tf_delta = timedelta(hours=1)
        elif timeframe == '4h': tf_delta = timedelta(hours=4)
        elif timeframe == '1d': tf_delta = timedelta(days=1)
        else: return data # Unknown timeframe, skip
        
        filled = []
        for i in range(len(data) - 1):
            curr = data[i]
            next_candle = data[i+1]
            filled.append(curr)
            
            # Check gap
            curr_time = datetime.fromisoformat(curr['time'])
            next_time = datetime.fromisoformat(next_candle['time'])
            
            diff = next_time - curr_time
            if diff > tf_delta * 1.5: # Tolerance
                # Missing candles count
                missing_count = int(diff / tf_delta) - 1
                if missing_count > 0:
                    step_price = (next_candle['close'] - curr['close']) / (missing_count + 1)
                    
                    for k in range(1, missing_count + 1):
                        interp_time = curr_time + (tf_delta * k)
                        interp_price = curr['close'] + (step_price * k)
                        
                        # Create Synthetic Candle
                        filled.append({
                            "time": interp_time.isoformat(),
                            "open": interp_price,
                            "high": interp_price,
                            "low": interp_price,
                            "close": interp_price,
                            "volume": 0 # Synthetic
                        })
                        
        filled.append(data[-1])
        return filled

    def _fetch_sql(self, symbol: str, start: datetime, end: datetime, timeframe: str):
        conn = psycopg2.connect(settings.DATABASE_URL)
        cursor = conn.cursor()
        
        query = """
            SELECT time, open, high, low, close, volume
            FROM ohlcv
            WHERE (symbol = %s OR symbol = %s) 
            AND timeframe = %s 
            AND time >= %s 
            AND time <= %s
            ORDER BY time ASC
        """
        cursor.execute(query, (symbol, symbol.replace('/',''), timeframe, start, end))
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "time": r[0].isoformat(),
                "open": float(r[1]),
                "high": float(r[2]),
                "low": float(r[3]),
                "close": float(r[4]),
                "volume": float(r[5])
            }
            for r in rows
        ]

    def _fetch_bq(self, symbol: str, start: datetime, end: datetime, timeframe: str):
        # Format for BQ
        start_str = start.strftime('%Y-%m-%d %H:%M:%S')
        end_str = end.strftime('%Y-%m-%d %H:%M:%S')
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        query = f"""
            SELECT time, open, high, low, close, volume
            FROM `{project_id}.maelstrom.market_history_cold`
            WHERE symbol = '{symbol}' AND timeframe = '{timeframe}' 
            AND time >= '{start_str}' AND time <= '{end_str}'
            ORDER BY time ASC
        """
        try:
            query_job = self.bq_client.query(query)
            return [
                {
                    "time": row.time.isoformat(),
                    "open": float(row.open),
                    "high": float(row.high),
                    "low": float(row.low),
                    "close": float(row.close),
                    "volume": float(row.volume)
                }
                for row in query_job
            ]
        except Exception:
            return []

market_provider = MarketDataProvider()
