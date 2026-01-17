"""
TURBO-PLAN X - Pydantic Models for API Request/Response
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Market Data Models

class TickerResponse(BaseModel):
    """Real-time ticker data"""
    symbol: str
    last: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    volume: Optional[float] = None
    change_24h: Optional[float] = None
    timestamp: int
    datetime: Optional[str] = None


class OHLCVCandle(BaseModel):
    """OHLCV candlestick data"""
    time: int = Field(..., description="Unix timestamp in milliseconds")
    open: float
    high: float
    low: float
    close: float
    volume: float


class OHLCVResponse(BaseModel):
    """Historical OHLCV response"""
    symbol: str
    timeframe: str
    candles: List[OHLCVCandle]
    count: int


class OrderBookLevel(BaseModel):
    """Single order book level [price, quantity]"""
    price: float
    quantity: float


class OrderBookResponse(BaseModel):
    """Order book depth"""
    symbol: str
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    timestamp: int


class TradeData(BaseModel):
    """Recent trade data"""
    id: Optional[str] = None
    timestamp: int
    price: float
    amount: float
    side: str = Field(..., description="buy or sell")
    cost: Optional[float] = None


class MarketScreenerItem(BaseModel):
    """Market screener item"""
    symbol: str
    last: float
    change_24h: float
    volume: float
    high: float
    low: float


class MarketStats(BaseModel):
    """Quantum Market Statistics"""
    symbol: str
    volatility: float
    momentum: float
    trend_strength: float
    sentiment: float
    timestamp: int


# AI Models

class AIPrediction(BaseModel):
    """AI prediction for a symbol"""
    symbol: str
    prediction: str = Field(..., description="BUY, SELL, or HOLD")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    predicted_price: Optional[float] = None
    timeframe: str = "24h"
    model_name: str = "default"
    timestamp: int


# Agent Models

class AgentStatus(BaseModel):
    """AI agent status"""
    agent_id: str
    agent_type: str = Field(..., description="scout, analyst, hunter, defender")
    status: str = "active"
    last_action: Optional[str] = None
    performance_score: Optional[float] = None


class HiveMindStatus(BaseModel):
    """Overall Hive-Mind status"""
    total_agents: int
    active_agents: int
    agents_by_type: dict
    last_update: datetime


# Health Check

class HealthResponse(BaseModel):
    """API health check response"""
    status: str = "healthy"
    version: str
    database: str = "connected"
    redis: str = "connected"
    timestamp: datetime


# Error Models

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime
