import asyncio
import websockets
import json
import redis.asyncio as redis
import os

REDIS_URL = "redis://localhost:6379"
STREAMS = [
    "btcusdt@kline_1m",
    "ethusdt@kline_1m",
    "solusdt@kline_1m"
]
BINANCE_WS = f"wss://stream.binance.com:9443/stream?streams={'/'.join(STREAMS)}"

async def producer():
    r = redis.from_url(REDIS_URL)
    print(f"🔌 Connecting to Redis at {REDIS_URL}")
    print(f"🔌 Connecting to Binance WS: {BINANCE_WS}")
    
    async with websockets.connect(BINANCE_WS) as ws:
        print("✅ Connected to Binance WebSocket.")
        while True:
            try:
                message = await ws.recv()
                data = json.loads(message)
                
                # Extract relevant data
                # Payload format: {"stream": "...", "data": {...}}
                stream = data['stream']
                payload = data['data']
                kline = payload['k']
                
                symbol = kline['s']
                close_price = kline['c']
                is_closed = kline['x']
                
                # Push to Redis Stream
                # Key: 'market_stream', Fields: symbol, price, timestamp
                entry_id = await r.xadd('market_stream', {
                    'symbol': symbol,
                    'price': close_price,
                    'timestamp': str(payload['E']),
                    'is_closed': '1' if is_closed else '0'
                })
                
                print(f"📡 {symbol} ${close_price} -> Redis ID: {entry_id}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(producer())
    except KeyboardInterrupt:
        print("Stopped.")
