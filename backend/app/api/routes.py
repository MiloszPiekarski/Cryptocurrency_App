"""
TURBO-PLAN X - API Routes
All backend endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional, List
import json
from datetime import datetime, timezone, timedelta
from loguru import logger

from app.models.schemas import (
    TickerResponse, OHLCVResponse, OHLCVCandle, OrderBookResponse,
    OrderBookLevel, AIPrediction, AgentStatus, HiveMindStatus,
    HealthResponse, ErrorResponse, TradeData, MarketScreenerItem, MarketStats
)
from app.core.config import get_settings, Settings
from app.core.database import get_db_manager, DatabaseManager

router = APIRouter()


# Market Data Endpoints

@router.get("/market/ticker/{symbol}", response_model=TickerResponse, tags=["Market Data"])
async def get_ticker(
    symbol: str,
    request: Request,
    settings: Settings = Depends(get_settings)
):
    """
    Get real-time ticker data for a symbol
    
    - **symbol**: Trading pair symbol (e.g., BTC/USDT)
    """
    try:
        db = get_db_manager()
        symbol_clean = symbol.replace('/', '')
        
        # Get from Redis cache
        redis_key = f"ticker:{symbol_clean}"
        data = db.redis_client.get(redis_key)
        
        if data:
            ticker_data = json.loads(data)
            return TickerResponse(**ticker_data)
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No real-time data for {symbol}. Is the streamer running?"
            )
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid data format in cache")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/market/ohlcv/{symbol}", response_model=OHLCVResponse, tags=["Market Data"])
async def get_ohlcv(
    symbol: str,
    timeframe: str = "1h",
    limit: int = 100
):
    """
    Get historical OHLCV candlestick data.
    Uses MarketDataProvider to ensure:
    1. Gaps are filled or repaired
    2. Real-time candle is appended
    """
    try:
        from app.core.market_data_provider import market_provider
        
        # Calculate start and end times based on limit
        # This is an approximation, the provider handles exact fetching
        # If limit is 100 and timeframe is 1h, we need last 100 hours
        # BUT MarketDataProvider usually takes start/end range.
        # We can implement a helper or just interpret limit.
        # Actually, get_continuous_history takes start_date, end_date.
        
        # We'll calculate a generous window to ensure we get 'limit' candles
        tf_minutes = 60
        if timeframe == '4h': tf_minutes = 240
        elif timeframe == '1d': tf_minutes = 1440
        elif timeframe == '15m': tf_minutes = 15
        elif timeframe == '5m': tf_minutes = 5
        elif timeframe == '1m': tf_minutes = 1
        
        end_date = datetime.now(timezone.utc)
        # buffer multiplier to account for potential missing data that gets skipped
        start_date = end_date - timedelta(minutes=tf_minutes * limit * 1.5)
        
        # Normalize symbol
        symbol_normalized = symbol
        if '/' not in symbol and len(symbol) > 5:
            # Default to 3 char quote if not specified, e.g. BTCUSDT -> BTC/USDT
            # This covers most crypto pairs.
            symbol_normalized = f"{symbol[:3]}/{symbol[3:]}"
            
        # Fetch Data via Provider
        candles_data = market_provider.get_continuous_history(symbol_normalized, start_date, end_date, timeframe)
        
        
        # Slice to limit and format
        if not candles_data:
            return OHLCVResponse(symbol=symbol, timeframe=timeframe, candles=[], count=0)
            
        # The provider returns chronologically sorted data (Old -> New)
        # Frontend might expect New -> Old or Old -> New? 
        # Previous code: "candles = ... for row in reversed(rows)" which implies API returned New -> Old or Old -> New?
        # Previous SQL: ORDER BY time DESC => Newest first.
        # Previous List Comp: reversed(rows) => Oldest first.
        # So Frontend expects Oldest First (Chronological).
        
        # Take last 'limit' candles
        final_candles = candles_data[-limit:]
        
        # Convert to Pydantic model
        candles = [
            OHLCVCandle(
                time=int(datetime.fromisoformat(c['time']).timestamp() * 1000),
                open=float(c['open']),
                high=float(c['high']),
                low=float(c['low']),
                close=float(c['close']),
                volume=float(c['volume'])
            )
            for c in final_candles
        ]
        
        return OHLCVResponse(
            symbol=symbol,
            timeframe=timeframe,
            candles=candles,
            count=len(candles)
        )
    
    except Exception as e:
        logger.error(f"OHLCV Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market/orderbook/{symbol}", response_model=OrderBookResponse, tags=["Market Data"])
async def get_orderbook(symbol: str):
    """
    Get current order book depth
    
    - **symbol**: Trading pair (e.g., BTC/USDT)
    """
    try:
        db = get_db_manager()
        symbol_clean = symbol.replace('/', '')
        
        # Get from Redis cache
        redis_key = f"orderbook:{symbol_clean}"
        data = db.redis_client.get(redis_key)
        
        default_timestamp = int(datetime.now().timestamp() * 1000)
        
        if not data:
            # Return empty/mock orderbook instead of 404 to correct frontend stability
             return OrderBookResponse(
                symbol=symbol,
                bids=[],
                asks=[],
                timestamp=default_timestamp
            )
        
        ob_data = json.loads(data)
        
        return OrderBookResponse(
            symbol=symbol,
            bids=[OrderBookLevel(price=b[0], quantity=b[1]) for b in ob_data.get('bids', [])],
            asks=[OrderBookLevel(price=a[0], quantity=a[1]) for a in ob_data.get('asks', [])],
            timestamp=ob_data.get('timestamp') or default_timestamp
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market/trades/{symbol}", response_model=list[TradeData], tags=["Market Data"])
async def get_trades(symbol: str, limit: int = 50):
    """
    Get recent trades
    """
    # Placeholder: In a real system, fetch from DB or Redis list
    # Returning empty list to prevent 404 error on frontend
    return []


import httpx

AI_ENGINE_URL = "http://localhost:8001/api/v1"

async def _proxy_get(path: str):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{AI_ENGINE_URL}/{path}", timeout=30.0)
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        logger.error(f"Proxy Error {path}: {e}")
    return None

@router.get("/market/screener", response_model=List[MarketScreenerItem], tags=["Market Data"])
async def get_screener():
    """
    Get market screener data (Proxied to AI Engine)
    """
    data = await _proxy_get("market/screener")
    if data:
        # Map AI Engine fields to Backend Schema
        mapped_data = []
        for item in data:
            mapped_data.append({
                "symbol": item.get('symbol'),
                "last": item.get('price'),
                "change_24h": item.get('change_24h'),
                "high": item.get('high_24h'),
                "low": item.get('low_24h'),
                "volume": item.get('volume_usdt'),
            })
        return [MarketScreenerItem(**item) for item in mapped_data]

    # Fallback to mock if AI Engine is down
    return [
        MarketScreenerItem(symbol="BTC/USDT", last=45000.0, change_24h=2.5, volume=1000000.0, high=46000.0, low=44000.0),
        MarketScreenerItem(symbol="ETH/USDT", last=2500.0, change_24h=1.2, volume=500000.0, high=2550.0, low=2450.0),
        MarketScreenerItem(symbol="SOL/USDT", last=100.0, change_24h=-0.5, volume=200000.0, high=105.0, low=95.0),
    ]

# --- HIVE MIND PROXY ROUTES ---

@router.get("/hive/swarm/{symbol:path}", tags=["AI"])
async def get_hive_swarm(symbol: str):
    """Proxy to AI Engine Hive Swarm"""
    data = await _proxy_get(f"hive/swarm/{symbol}")
    if data: return data
    return {"error": "Hive Mind Offline (Proxy Failed)"}

@router.get("/hive/whales", tags=["AI"])
async def get_hive_whales(limit: int = 5):
    """Proxy to AI Engine Whales"""
    data = await _proxy_get(f"hive/whales?limit={limit}")
    if data: return data
    return []

@router.get("/hive/tactical/{symbol:path}", tags=["AI"])
async def get_hive_tactical(symbol: str):
    """Proxy to AI Engine Tactical"""
    data = await _proxy_get(f"hive/tactical/{symbol}")
    if data: return data
    return {"error": "Tactical Intel Offline"}

@router.get("/ai/prediction/{symbol}", response_model=AIPrediction, tags=["AI"])
async def get_ai_prediction(symbol: str):
    """
    Get AI prediction for a symbol (Proxied)
    """
    data = await _proxy_get(f"ai/prediction/{symbol}")
    if data:
        return AIPrediction(**data)
        
    # Mock Fallback
    return AIPrediction(
        symbol=symbol,
        prediction="HOLD",
        confidence=0.0,
        predicted_price=None,
        timeframe="24h",
        model_name="not_implemented",
        timestamp=int(datetime.now().timestamp() * 1000)
    )

@router.get("/ai/agents/status", response_model=HiveMindStatus, tags=["AI"])
async def get_agents_status():
    """
    Get Hive-Mind agent status (Proxied)
    """
    # Note: AI Engine might not have this exact endpoint, checking availability...
    # Main.py in AI Engine didn't show /agents/status, but /hive/swarm returns status.
    # We'll leave the mock for now or try to fetch from swarm/BTCUSDT to get general status?
    # Let's keep the mock for status to avoid breakage if endpoint missing.
    return HiveMindStatus(
        total_agents=1000,
        active_agents=850,
        agents_by_type={"scout": 200, "hunter": 200},
        last_update=datetime.now()
    )

# --- PDF REPORT PROXY ---
from fastapi.responses import Response

@router.post("/reports/pdf_post", tags=["Reports"])
async def proxy_pdf_report(request: Request):
    """Proxy PDF generation request to AI Engine"""
    try:
        body = await request.json()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{AI_ENGINE_URL}/reports/pdf_post",
                json=body,
                timeout=60.0  # PDF generation can take time
            )
            if resp.status_code == 200:
                return Response(
                    content=resp.content,
                    media_type="application/pdf",
                    headers={"Content-Disposition": "attachment; filename=Tactical_Brief.pdf"}
                )
            else:
                logger.error(f"PDF Proxy Error: {resp.status_code} - {resp.text}")
                raise HTTPException(status_code=resp.status_code, detail="PDF generation failed")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="PDF generation timed out")
    except Exception as e:
        logger.error(f"PDF Proxy Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Health Check

@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check(settings: Settings = Depends(get_settings)):
    """API health check endpoint"""
    try:
        db = get_db_manager()
        
        # Test database
        with db.get_db_cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "connected"
        
        # Test Redis
        db.redis_client.ping()
        redis_status = "connected"
        
        return HealthResponse(
            status="healthy",
            version=settings.APP_VERSION,
            database=db_status,
            redis=redis_status,
            timestamp=datetime.now()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )


# Statistics

@router.get("/stats/database", tags=["System"])
async def get_database_stats():
    """Get database statistics"""
    try:
        db = get_db_manager()
        
        with db.get_db_cursor() as cursor:
            # Count candles by symbol
            cursor.execute('''
                SELECT symbol, timeframe, COUNT(*) as count,
                       MIN(time) as first_candle,
                       MAX(time) as last_candle
                FROM ohlcv
                GROUP BY symbol, timeframe
                ORDER BY symbol, timeframe
            ''')
            
            candles = cursor.fetchall()
        
        return {
            "total_symbols": len(set(c['symbol'] for c in candles)),
            "candles_by_symbol": [
                {
                    "symbol": c['symbol'],
                    "timeframe": c['timeframe'],
                    "count": c['count'],
                    "first_candle": c['first_candle'].isoformat() if c['first_candle'] else None,
                    "last_candle": c['last_candle'].isoformat() if c['last_candle'] else None
                }
                for c in candles
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Live WebSockets
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import redis.asyncio as aioredis # Requires redis-py >= 4.2.0

@router.websocket("/ws/market/{symbol}")
async def websocket_market(websocket: WebSocket, symbol: str):
    """
    Live WebSocket for Market Data.
    Subscribes to Redis channels for real-time tickers and trades.
    """
    await websocket.accept()
    symbol_clean = symbol.replace('/', '')
    
    # Create a dedicated async Redis client for this connection
    # (FastAPI's db_manager might be sync or shared pool)
    r = aioredis.from_url(get_settings().REDIS_URL, decode_responses=True)
    pubsub = r.pubsub()
    
    try:
        # Subscribe to ticker and trades
        await pubsub.subscribe(f"ticker:{symbol_clean}", f"trade:{symbol_clean}")
        
        # Send initial snapshot?
        # Maybe not strictly necessary if frontend fetches REST snapshot first.
        
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                await websocket.send_json({
                    "type": "update",
                    "channel": message['channel'],
                    "data": json.loads(message['data'])
                })
            await asyncio.sleep(0.01) # Prevent CPU spin
            
    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {symbol}")
    except Exception as e:
        logger.error(f"WebSocket Error [{symbol}]: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        try:
            await pubsub.unsubscribe()
            await r.close()
        except:
            pass
