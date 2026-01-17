"""
TURBO-PLAN X - Main FastAPI Application
Professional backend server with WebSocket support
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from loguru import logger
import asyncio
import json
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.database import DatabaseManager, db_manager as global_db_manager
from app.api import routes

from app.services.user_service import UserService
from app.api import user

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("Starting TURBO-PLAN X API...")
    
    # Initialize database manager
    from app.core import database
    database.db_manager = DatabaseManager(
        database_url=settings.DATABASE_URL,
        redis_url=settings.REDIS_URL
    )
    database.db_manager.initialize()
    
    # Init tables
    try:
        UserService.init_table()
    except Exception as e:
        logger.error(f"Failed to init users table: {e}")
    
    logger.success("✓ Database connections initialized")
    logger.success(f"✓ API running on {settings.HOST}:{settings.PORT}")
    
    yield
    
    # Cleanup
    logger.info("Shutting down...")
    database.db_manager.close()
    logger.success("✓ Cleanup complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered cryptocurrency trading platform backend API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Statistics Endpoint
from app.core.statistics_module import get_stats_for

@app.get("/api/statistics/{symbol:path}")
async def get_statistics(symbol: str):
    """
    Get mathematical analysis for a symbol (e.g. BTC/USDT).
    Includes Mean, Variance, LatEX formulas.
    """
    try:
        # Handle slash in symbol for URL path (e.g. BTC%2FUSDT) or just replace
        decoded_symbol = symbol.replace('-', '/') # Frontend might send BTC-USDT
        stats = get_stats_for(decoded_symbol)
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"Stats Error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


# Unified History Endpoint
from app.core.market_data_provider import market_provider

@app.get("/api/v1/market/unified-history/{symbol:path}")
async def get_unified_history(symbol: str, timeframe: str = '4h', limit: int = 100):
    """
    Get continuous market history from Hot + Cold storage.
    """
    try:
        decoded_symbol = symbol.replace('-', '/')
        end_date = datetime.now(timezone.utc)
        # Calculate start based on limit/tf? Or just last N
        # Simplified: limit -> days
        days = (limit * 4) / 24 if timeframe == '4h' else (limit/24) # approx
        if timeframe == '1h': days = limit / 24
        elif timeframe == '1d': days = limit
        
        start_date = end_date - timedelta(days=days + 1)
        
        data = market_provider.get_continuous_history(decoded_symbol, start_date, end_date, timeframe)
        return JSONResponse(content=data)
    except Exception as e:
        logger.error(f"Unified History Error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Include API routes
app.include_router(routes.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """API root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs": "/docs",
        "health": "/api/v1/health",
        "timestamp": datetime.now().isoformat()
    }


# WebSocket for real-time market updates
@app.websocket("/ws/market")
async def websocket_market(websocket: WebSocket):
    """
    WebSocket endpoint for real-time market data
    
    Streams live ticker updates from Redis pub/sub
    """
    await websocket.accept()
    logger.info("WebSocket client connected")
    
    try:
        from app.core.database import get_db_manager
        db = get_db_manager()
        
        # Subscribe to Redis pub/sub
        pubsub = db.redis_client.pubsub()
        pubsub.subscribe('market:tickers')
        
        # Send initial connection success message
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket connected to TURBO-PLAN X",
            "timestamp": datetime.now().isoformat()
        })
        
        # Listen for messages
        async def listen_redis():
            """Listen to Redis pub/sub in background"""
            try:
                for message in pubsub.listen():
                    if message['type'] == 'message':
                        await websocket.send_text(message['data'])
            except Exception as e:
                logger.error(f"Redis listen error: {e}")
        
        # Create background task
        listen_task = asyncio.create_task(listen_redis())
        
        # Keep connection alive and handle client messages
        try:
            while True:
                data = await websocket.receive_text()
                # Echo back or handle commands
                await websocket.send_json({
                    "type": "echo",
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                })
        except WebSocketDisconnect:
            logger.info("WebSocket client disconnected")
            listen_task.cancel()
        finally:
            pubsub.unsubscribe('market:tickers')
            pubsub.close()
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "detail": "The requested resource was not found",
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )


# Run server if executed directly
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
