import ccxt
import pandas as pd
import pandas_ta as ta
import time
from datetime import datetime

class MarketDataManager:
    def __init__(self):
        # Initialize multiple exchanges for fallback
        self.exchanges = {
            'binance': ccxt.binance({
                'enableRateLimit': True,
                'options': {'defaultType': 'future'}
            }),
            'bitget': ccxt.bitget({
                'enableRateLimit': True,
                'options': {'defaultType': 'future'}
            }),
            'okx': ccxt.okx({
                'enableRateLimit': True
            })
        }
        self.primary_exchange = 'binance'
        self._price_cache = {}
        self._ohlcv_cache = {}

    def _safe_fetch(self, method_name, symbol, *args, **kwargs):
        """Generic fallback wrapper for exchange methods"""
        clean_symbol = symbol.replace('USDT', '/USDT') if '/' not in symbol else symbol
        
        # Try primary first
        order = [self.primary_exchange] + [ex for ex in self.exchanges.keys() if ex != self.primary_exchange]
        
        last_error = None
        for ex_id in order:
            try:
                exchange = self.exchanges[ex_id]
                method = getattr(exchange, method_name)
                # print(f"DEBUG: Trying {ex_id} for {method_name} {clean_symbol}")
                return method(clean_symbol, *args, **kwargs)
            except Exception as e:
                last_error = e
                # print(f"DEBUG: {ex_id} failed: {e}")
                continue
        
        raise Exception(f"All exchanges failed for {method_name}: {last_error}")

    def get_price(self, symbol: str):
        """Fetch real-time price with fallback"""
        now = time.time()
        if symbol in self._price_cache:
            cache_time, data = self._price_cache[symbol]
            if now - cache_time < 5:
                return data

        try:
            ticker = self._safe_fetch('fetch_ticker', symbol)
            result = {
                "symbol": symbol,
                "price": ticker['last'],
                "change_24h": ticker['percentage'],
                "high_24h": ticker['high'],
                "low_24h": ticker['low'],
                "volume_24h": ticker['baseVolume'] or ticker['quoteVolume'],
                "timestamp": ticker['timestamp']
            }
            self._price_cache[symbol] = (now, result)
            return result
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            if symbol in self._price_cache:
                return self._price_cache[symbol][1]
            return None

    def get_ohlcv(self, symbol: str, timeframe='1h', limit=100):
        """Fetch OHLCV candles with fallback"""
        try:
            ohlcv = self._safe_fetch('fetch_ohlcv', symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Indicators
            df.ta.rsi(length=14, append=True)
            df.ta.macd(append=True)
            df.ta.ema(length=50, append=True)
            df.ta.ema(length=200, append=True)
            return df
        except Exception as e:
            print(f"Error fetching OHLCV for {symbol}: {e}")
            return pd.DataFrame()

    def get_orderbook(self, symbol: str, limit: int = 10):
        """Fetch Order Book with fallback"""
        try:
            orderbook = self._safe_fetch('fetch_order_book', symbol, limit)
            return {
                "symbol": symbol,
                "bids": [{"price": price, "quantity": amount} for price, amount in orderbook['bids']],
                "asks": [{"price": price, "quantity": amount} for price, amount in orderbook['asks']],
                "timestamp": orderbook['timestamp']
            }
        except Exception as e:
            print(f"Orderbook Error {symbol}: {e}")
            return None

    def get_trades(self, symbol: str, limit: int = 50):
        """Fetch Trades with fallback"""
        try:
            trades = self._safe_fetch('fetch_trades', symbol, limit=limit)
            return [
                {
                    "id": t['id'],
                    "timestamp": t['timestamp'],
                    "price": t['price'],
                    "amount": t['amount'],
                    "side": t['side'],
                    "cost": t['cost'] or (t['price'] * t['amount'])
                }
                for t in trades
            ]
        except Exception as e:
            print(f"Trades Error {symbol}: {e}")
            return []

    def get_top_symbols(self, limit: int = 20):
        """Fetch Top Markets (tries Binance first, then fallback)"""
        try:
            # Special case for fetch_tickers as it's large
            tickers = self._safe_fetch('fetch_tickers', '') # Empty symbol for all
            valid_tickers = [
                t for t in tickers.values() 
                if '/USDT' in t['symbol'] and 'UP/' not in t['symbol'] and 'DOWN/' not in t['symbol']
            ]
            sorted_tickers = sorted(valid_tickers, key=lambda x: x['quoteVolume'] or 0, reverse=True)
            
            top_tickers = []
            for t in sorted_tickers[:limit]:
                raw_symbol = t['symbol']
                clean_symbol = raw_symbol.split(':')[0] if ':' in raw_symbol else raw_symbol
                top_tickers.append({
                    "symbol": clean_symbol,
                    "last": t['last'],
                    "change_24h": t['percentage'],
                    "volume": t['quoteVolume'] or 0,
                    "high": t['high'],
                    "low": t['low']
                })
            return top_tickers
        except Exception as e:
            print(f"Screener Error: {e}")
            return []

# Singleton Instance
market_data = MarketDataManager()
