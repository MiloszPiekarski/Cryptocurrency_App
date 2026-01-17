import ccxt.async_support as ccxt
import pandas as pd
import numpy as np
import asyncio
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScreenerService:
    def __init__(self):
        # Switched to Bybit to bypass Binance IP Ban (418)
        self.exchange = ccxt.bybit({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
            }
        })
        self._cache = None
        self._last_cache_time = 0
        self._cache_ttl = 30
        self._fetch_lock = asyncio.Lock()

    async def get_top_cryptos(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Fetches Top 20 cryptocurrencies. Caches the heavy TA/Sparkline data.
        """
        import time
        current_time = time.time()
        
        # 1. First Check (Fast)
        if self._cache and (current_time - self._last_cache_time < self._cache_ttl):
            logger.info("Serving screener data from cache (hit)")
            return self._cache

        # 2. Acquire Lock
        async with self._fetch_lock:
            # 3. Second Check (Safety)
            if self._cache and (time.time() - self._last_cache_time < self._cache_ttl):
                logger.info("Serving screener data from cache (after lock)")
                return self._cache

            try:
                logger.info("Fetching fresh screener data from Bybit...")
                # 1. Fetch Tickers to find Top Volume pairs
                tickers = await self.exchange.fetch_tickers()
                
                # Filter for USDT pairs only and exclude leveraged tokens
                excluded_coins = ['UP/', 'DOWN/', 'BULL/', 'BEAR/', 'USDC/', 'USD1/', 'FDUSD/', 'TUSD/', 'USDP/', 'DAI/']
                usdt_pairs = [
                    ticker for symbol, ticker in tickers.items() 
                    if symbol.endswith('USDT') 
                    and all(x not in symbol for x in excluded_coins)
                ]
                
                # Sort by Quote Volume (volume in USDT) descending
                sorted_pairs = sorted(usdt_pairs, key=lambda x: x['quoteVolume'], reverse=True)
                top_pairs = sorted_pairs[:limit]
                
                # 2. Process each pair
                tasks = [self._process_pair(pair) for pair in top_pairs]
                results = await asyncio.gather(*tasks)
                
                final_data = [r for r in results if r is not None]
                
                # Update cache
                if final_data:
                    self._cache = final_data
                    self._last_cache_time = current_time
                    
                return final_data

            except Exception as e:
                logger.error(f"Error serving screener data: {e}")
                return []
            finally:
                # Can't close exchange here if singleton? 
                # Actually, duplicate close might be issues if we reuse the instance?
                # ScreenerService is usually singleton.
                # If we close, next call might fail?
                # CCXT exchange close usually closes session.
                # Better NOT to close if the service is long-lived.
                # But wait, previous code had `await self.exchange.close()`.
                # If it's closed, does it reopen?
                # CCXT usually manages it.
                # Let's keep it safe: Don't close for now, or check internal state.
                # But if I don't close, I might leak sessions?
                # Given I am hitting rate limits, maybe I SHOULD close to reset?
                # But `__init__` is called once in `main.py`?
                # No, look at `main.py` usage.
                pass




    async def _process_pair(self, ticker_data: Dict[str, Any]) -> Dict[str, Any] | None:
        symbol = ticker_data['symbol']
        try:
            # Fetch Daily candles for SMA 200 (need at least 200 candles)
            # Limit 300 to be safe and have enough data for calculation
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe='1d', limit=300)
            
            if not ohlcv:
                return None

            # Create DataFrame for easier calculation
            # Columns: [Timestamp, Open, High, Low, Close, Volume]
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Sparkline: visual representation of the trend (last 30 days is usually good for daily)
            sparkline = df['close'].tail(30).tolist()

            # Basic Metrics
            current_price = ticker_data['last']
            change_24h = ticker_data['percentage']
            volume = ticker_data['quoteVolume']
            high_24h = ticker_data['high']
            low_24h = ticker_data['low']
            
            # Calculate Deterministic Quant Score
            score_data = self._calculate_asset_score(df)
            
            # Simple Name Mapping
            name_map = {
                "BTC": "Bitcoin", "ETH": "Ethereum", "BNB": "Binance Coin",
                "SOL": "Solana", "XRP": "Ripple", "ADA": "Cardano",
                "DOGE": "Dogecoin", "DOT": "Polkadot", "MATIC": "Polygon",
                "AVAX": "Avalanche", "TRX": "Tron", "LTC": "Litecoin"
            }
            base_symbol = symbol.split('/')[0]

            return {
                "symbol": base_symbol,
                "name": name_map.get(base_symbol, base_symbol),
                "price": current_price,
                "change_24h": change_24h,
                "low_24h": low_24h,
                "high_24h": high_24h,
                "volume_usdt": volume,
                "sparkline_7d": sparkline,
                "trend_sparkline": sparkline, # Requested format
                "quant_score": score_data['ai_confidence'],
                "ai_confidence": score_data['ai_confidence'], # Kept for compat
                "confidence": score_data['ai_confidence'], # Requested new name
                "signal": score_data['signal']
            }

        except Exception as e:
            logger.warning(f"Failed to process {symbol}: {e}")
            return None

    def _calculate_asset_score(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculates a deterministic 0-100 score based on technical indicators.
        Logic (The Real Math):
        Start = 50 pts
        RSI (14): < 30 (+20), > 70 (-20)
        Trend: Price > SMA 50 (+15), Price < SMA 50 (-15)
        Momentum: Price > SMA 200 (+10)
        Volume: Vol > 1.5 * AvgVol20 (+10)
        """
        try:
            # Ensure we have enough data
            if len(df) < 200:
                # Not enough data for SMA 200, return generic neutral
                return {"ai_confidence": 50, "signal": "NEUTRAL"}

            closes = df['close']
            volumes = df['volume']
            current_close = closes.iloc[-1]
            current_vol = volumes.iloc[-1]

            # --- KROK 1 (Wskaźniki) ---

            # 1. RSI (14)
            delta = closes.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi_val = rsi.iloc[-1]

            # 2. SMA (50) and SMA (200)
            sma_50 = closes.rolling(window=50).mean().iloc[-1]
            sma_200 = closes.rolling(window=200).mean().iloc[-1]

            # 3. Volume Average (20)
            vol_sma_20 = volumes.rolling(window=20).mean().iloc[-1]

            # --- KROK 2 (Scoring - Punktacja 0-100) ---
            
            score = 50  # Start Neutral

            # RSI Score
            if rsi_val < 30:
                score += 20  # Oversold -> Bounce likely (Bullish)
            elif rsi_val > 70:
                score -= 20  # Overbought -> Corection likely (Bearish)
            
            # Trend Score (SMA 50)
            if current_close > sma_50:
                score += 15 # Bullish Trend
            else:
                score -= 15 # Bearish Trend

            # Momentum Score (SMA 200)
            if current_close > sma_200:
                score += 10 # Long term Bullish
            # No penalty for being below SMA 200 in this logic, just no bonus

            # Volume Score
            if vol_sma_20 > 0 and current_vol > (1.5 * vol_sma_20):
                score += 10 # High volume confirming move

            # --- KROK 3 (Normalizacja i Etykiety) ---

            # Ensure 0-100
            final_score = int(np.clip(score, 0, 100))

            # Labels
            if final_score >= 61:
                signal = "BUY"
            elif final_score <= 40:
                signal = "SELL"
            else:
                signal = "NEUTRAL"

            return {
                "ai_confidence": final_score,
                "signal": signal
            }

        except Exception as e:
            logger.error(f"Error calculating score: {e}")
            return {"ai_confidence": 50, "signal": "ERROR"}
