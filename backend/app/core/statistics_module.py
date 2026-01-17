
import numpy as np
import scipy.stats as stats
from app.core.market_data_provider import market_provider
from datetime import datetime, timedelta, timezone

class MarketStatisticsProcessor:
    """
    Advanced Statistical Engine for CASH MAELSTROM.
    Calculates key metrics and provides mathematical transparency.
    Uses Unified Data Provider.
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.provider = market_provider

    def get_price_analysis(self, timeframe: str = '1h', limit: int = 168): # Default 1 week of hourly data
        # Calculate Date Range for Provider
        end_date = datetime.now(timezone.utc)
        # Approximate days needed
        days_needed = (limit * 1) if timeframe == '1h' else 7
        if timeframe == '4h': days_needed = limit * 4 / 24
        
        start_date = end_date - timedelta(days=days_needed + 5) # Buffer
        
        # Fetch Continuous Data
        data = self.provider.get_continuous_history(self.symbol, start_date, end_date, timeframe)
        
        # Limit manually
        if len(data) > limit:
            data = data[-limit:]
            
        if not data:
            return {"error": "No data available"}
        
        closes = [d['close'] for d in data]
        volumes = [d['volume'] for d in data]
        
        c_arr = np.array(closes)
        query_sql = f"SELECT close FROM ohlcv WHERE symbol='{self.symbol}' ORDER BY time DESC LIMIT {limit}"
        
        # 1. Central Tendency
        mean_val = np.mean(c_arr)
        median_val = np.median(c_arr)
        mode_res = stats.mode(c_arr, keepdims=True)
        mode_val = mode_res.mode[0] if len(mode_res.mode) > 0 else 0
        
        # 2. Dispersion
        var_val = np.var(c_arr)
        std_val = np.std(c_arr)
        
        # 3. Normalization (Min-Max)
        min_val = np.min(c_arr)
        max_val = np.max(c_arr)
        norm_data = (c_arr - min_val) / (max_val - min_val) if max_val > min_val else c_arr
        
        # 4. Histogram
        hist, bin_edges = np.histogram(c_arr, bins=10, density=True)
        
        # 5. Explanations (The "Show Math" feature)
        math_docs = {
            "mean": r"$$ \mu = \frac{1}{N} \sum_{i=1}^{N} x_i $$",
            "variance": r"$$ \sigma^2 = \frac{1}{N} \sum_{i=1}^{N} (x_i - \mu)^2 $$",
            "std_dev": r"$$ \sigma = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (x_i - \mu)^2} $$",
            "normalization": r"$$ z_i = \frac{x_i - \min(x)}{\max(x) - \min(x)} $$",
            "source_query": query_sql
        }
        
        return {
            "symbol": self.symbol,
            "samples": len(closes),
            "central_tendency": {
                "mean": float(mean_val),
                "median": float(median_val),
                "mode": float(mode_val)
            },
            "dispersion": {
                "variance": float(var_val),
                "std_dev": float(std_val),
                "range": float(max_val - min_val)
            },
            "histogram": {
                "counts": hist.tolist(),
                "bins": bin_edges.tolist()
            },
            "math_docs": math_docs,
            "latest_price": closes[0]
        }

# Helper
def get_stats_for(symbol: str):
    processor = MarketStatisticsProcessor(symbol)
    return processor.get_price_analysis()
