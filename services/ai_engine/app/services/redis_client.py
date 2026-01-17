import redis
import json

# Redis connection
# Zgodnie z planem: "Redis Streams -> Your AI"
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def get_latest_price(symbol: str):
    """
    Get latest price from Redis Stream 'market_stream'
    Ideally we would consume the stream via a worker, but for API lookup 
    we can utilize Redis XREVRANGE to get the last message.
    """
    try:
        # Get last entry from stream
        # Stream key defined in producer: 'market_stream'
        # We need to filter by symbol manually or assume producer splits streams.
        # Producer writes all to 'market_stream'.
        # XREVRANGE key max min COUNT 1
        last_entries = r.xrevrange('market_stream', count=10) # Fetch last 10 to find symbol
        
        clean_symbol = symbol.replace('/', '').upper() # BTC/USDT -> BTCUSDT
        
        for entry in last_entries:
            # entry is (id, {data})
            data = entry[1]
            if data['symbol'] == clean_symbol:
                return float(data['price'])
                
        return None
    except Exception as e:
        print(f"Redis Error: {e}")
        return None
