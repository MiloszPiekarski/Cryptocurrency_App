import ccxt
import time
import psycopg2
from datetime import datetime, timedelta, timezone
from cloud_config import CLOUD_SQL_CONNECTION_STRING

# Configure logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

# CONFIG
NOW = datetime.now(timezone.utc)
SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']

# User Requirements:
# - Minutowe: ostatnie 3 miesiące
# - Godzinowe: ostatnie 6 miesięcy
# - Tygodniowe: ostatni rok
# - Miesięczne: ostatnie 5 lat
TF_RANGES = {
    '1d':  timedelta(days=365),
    '1w':  timedelta(days=365*2),
    '1M':  timedelta(days=365*5), 
    '1h':  timedelta(days=180),
    '4h':  timedelta(days=180),
    '15m': timedelta(days=90),
    '30m': timedelta(days=90),
    '5m':  timedelta(days=90),
    '1m':  timedelta(days=90)
}

def rebuild():
    conn = psycopg2.connect(CLOUD_SQL_CONNECTION_STRING)
    cursor = conn.cursor()
    exchange = ccxt.okx()
    
    # OKX Mapping: usually matches CCXT defaults (BTC/USDT)
    SYMBOL_MAP = {
        'BTC/USDT': 'BTC/USDT', 
        'ETH/USDT': 'ETH/USDT', 
        'SOL/USDT': 'SOL/USDT'
    }
    
    # We truncate beforehand manually, or here:
    cursor.execute("TRUNCATE TABLE ohlcv")
    conn.commit()
    
    for symbol in SYMBOLS:
        okx_symbol = SYMBOL_MAP.get(symbol, symbol)
        logger.info(f"🏙️  {symbol} (Source: {okx_symbol})")
        
        for tf, delta in TF_RANGES.items():
            start_target = NOW - delta
            # We fetch from Source = Target - 1 Year
            start_source = start_target - timedelta(days=365)
            since = int(start_source.timestamp() * 1000)
            
            logger.info(f"   🚀 {tf} ({delta.days} days)")
            
            collected = 0
            while True:
                try:
                    # Fetch batch
                    ohlcv = exchange.fetch_ohlcv(okx_symbol, tf, since=since, limit=1000)
                    if not ohlcv: break
                    
                    records = []
                    for candle in ohlcv:
                        # Raw source time (2025)
                        st = datetime.fromtimestamp(candle[0]/1000, tz=timezone.utc)
                        # Precise shift
                        try:
                            tt = st.replace(year=st.year + 1)
                        except ValueError:
                            tt = st.replace(year=st.year + 1, day=28)
                        
                        if tt > NOW: continue
                        
                        records.append((tt, symbol, tf, candle[1], candle[2], candle[3], candle[4], candle[5]))
                    
                    if records:
                        args_str = ','.join(cursor.mogrify('(%s,%s,%s,%s,%s,%s,%s,%s)', x).decode('utf-8') for x in records)
                        cursor.execute(f"INSERT INTO ohlcv (time, symbol, timeframe, open, high, low, close, volume) VALUES {args_str} ON CONFLICT DO NOTHING")
                        conn.commit()
                        collected += len(records)
                        
                    # Update since
                    last_ts = ohlcv[-1][0]
                    if last_ts == since: 
                         since += 1 # force move
                    else:
                         since = last_ts + 1
                    
                    # If last target time >= NOW, we are done
                    # But if we collected 0 matching records because of time shift, we must continue!
                    # Logic Check: 'records' might be empty if all fetched candles are > NOW after shift.
                    # This happens if source is ahead of target.
                    
                    # Source Time of last candle
                    last_source_dt = datetime.fromtimestamp(last_ts/1000, tz=timezone.utc)
                    # Shifted
                    last_tt = last_source_dt.replace(year=last_source_dt.year + 1)
                    
                    if last_tt >= NOW: 
                        break
                    
                    time.sleep(0.5) # Kraken rate limit is strict
                except Exception as e:
                    logger.error(f"     ❌ {e}")
                    time.sleep(1)
                    since += 1000*60*60 # skip hour
            
            logger.info(f"      ✅ {collected} rows.")

    conn.close()
    logger.info("🎉 REBUILD COMPLETE.")

if __name__ == "__main__":
    rebuild()
