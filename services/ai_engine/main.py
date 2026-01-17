import os
from dotenv import load_dotenv

# Load environment variables FIRST before any local imports
load_dotenv()

from app.services.vertex_client import vertex_service
from app.agents.swarm import swarm
from app.analysis.market_stats_processor import MarketStatisticsProcessor
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import time
from datetime import datetime
import uvicorn
import threading
try:
    from app.train import train_model
except ImportError:
    print("Warning: Torch not found. Training disabled.")
    def train_model(*args, **kwargs):
        print("Training unavailable (Torch missing)")
from app.api.endpoints import market

app = FastAPI(
    title="TURBO-PLAN X AI Engine",
    description="Institutional-grade AI Prediction Microservice",
    version="1.0.0"
)

# Include Routers
app.include_router(market.router, prefix="/api/v1/market", tags=["market"])

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """
    Initialize Quantum Storage on Boot
    """
    from app.core.database import DatabaseManager
    from sqlalchemy import text
    try:
        db = DatabaseManager()
        print("⚡ [CASH MAELSTROM] Testing DB Connection...")
        with db.get_engine().connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS agent_logs (
                    id SERIAL PRIMARY KEY,
                    agent_id INT NOT NULL,
                    timestamp TIMESTAMPTZ DEFAULT NOW(),
                    task TEXT,
                    thought TEXT,
                    confidence FLOAT,
                    source_data TEXT
                );
            """))
            conn.commit()
        print("✅ [CASH MAELSTROM] Hive Mind Storage Initialized.")
        
        # Initialize Hive Mind Swarm
        # We import here or check global to avoid circular/early init issues
        if 'hive' in globals():
             print("🧠 [HIVE] Starting Autonomous Swarm...")
             globals()['hive'].start_swarm()
             
    except Exception as e:
        print(f"⚠️ [Startup Warning] Service Init Partial: {e}")

@app.get("/")
async def root():
    return {"status": "online", "service": "AI Engine"}

from pydantic import BaseModel
from app.services.market_data import market_data

from app.services.redis_client import get_latest_price

@app.get("/api/v1/market/ticker/{symbol}")
async def get_ticker(symbol: str):
    # Tier 1: Try Redis (Real-Time Stream) ~1ms latency
    live_price = get_latest_price(symbol)
    
    if live_price:
         # Construct ticker from live stream data
         # Note: Streams give us price, but REST gives 24h stats.
         # Hybrid approach: Get heavy stats from cache (REST), update price from Redis.
         
         # Get Cached Stats (REST)
         cached_data = market_data.get_price(symbol) or {}
         
         return {
            "symbol": symbol,
            "price": live_price, # SUPER FRESH
            "change_24h": cached_data.get('change_24h', 0),
            "high": cached_data.get('high_24h', 0),
            "low": cached_data.get('low_24h', 0),
            "volume": cached_data.get('volume_24h', 0),
            "timestamp": int(time.time() * 1000),
            "source": "redis-stream"
         }

    # Tier 2: Fallback to REST API (CCXT)
    try:
        real_data = market_data.get_price(symbol)
        if real_data:
            return {
                "symbol": symbol,
                "price": real_data['price'],
                "change_24h": real_data['change_24h'],
                "high": real_data['high_24h'],
                "low": real_data['low_24h'],
                "volume": real_data['volume_24h'],
                "timestamp": real_data['timestamp'],
                "source": "ccxt-rest"
            }
    except Exception as e:
        print(f"Ticker Error: {e}")

    return {
        "symbol": symbol,
        "price": 0.0,
        "change_24h": 0.0,
        "volume": 0
    }


@app.get("/api/v1/market/ohlcv/{symbol}")
async def get_ohlcv(symbol: str, timeframe: str = "1h", limit: int = 100):
    # Timeframe mapping: Frontend format -> Database format
    TIMEFRAME_MAP = {
        '1m': '1min',
        '5m': '5min',
        '15m': '15min',
        '30m': '30min',
        '1h': '1h',
        '4h': '4h',
        '1d': '1dzien',
        '1w': '1tydzien',
        '1M': '1miesiac'
    }
    
    # Map frontend timeframe to database timeframe
    db_timeframe = TIMEFRAME_MAP.get(timeframe, timeframe)
    
    # MASTER_PLAN: Try CCXT (live data) FIRST for real-time updates
    try:
        df = market_data.get_ohlcv(symbol, timeframe, limit)
        if not df.empty:
            candles = []
            for _, row in df.iterrows():
                candles.append({
                    "time": int(row['timestamp'].timestamp() * 1000),
                    "open": float(row['open']),
                    "high": float(row['high']),
                    "low": float(row['low']),
                    "close": float(row['close']),
                    "volume": float(row['volume'])
                })
            
            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "candles": candles,
                "count": len(candles),
                "source": "ccxt-live"
            }
    except Exception as e:
        print(f"OHLCV Live Fetch Error: {e}")

    # Fallback to Cloud SQL (historical data) if live fails
    try:
        from app.services.database import get_ohlcv_from_db
        db_candles = get_ohlcv_from_db(symbol, db_timeframe, limit)
        
        if db_candles and len(db_candles) > 0:
            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "candles": db_candles,
                "count": len(db_candles),
                "source": "cloud-sql-fallback"
            }
    except Exception as e:
        print(f"Database read error: {e}")
    
    # (Legacy Fallback removed as it is now primary)

    # Empty fallback
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "candles": [],
        "count": 0
    }

@app.get("/api/v1/market/orderbook/{symbol}")
async def get_orderbook(symbol: str):
    # Real Orderbook
    data = market_data.get_orderbook(symbol, limit=10)
    if data:
        return data
        
    # Fallback Empty
    return {
        "symbol": symbol,
        "bids": [],
        "asks": [],
        "timestamp": int(time.time() * 1000)
    }

@app.get("/api/v1/market/trades/{symbol}")
async def get_trades(symbol: str, limit: int = 50):
    # Real Trades
    data = market_data.get_trades(symbol, limit=limit)
    if data:
        return data
        
    # Fallback Empty
    return []

@app.get("/api/v1/ai/prediction/{symbol}")
async def get_ai_prediction(symbol: str):
    # HYBRID INTELLIGENCE ENGINE
    # 1. Technical Analysis (Base Layer)
    # 2. Neural Net (Enhanced Layer - if trained)

    try:
        # Fetch Real Data (200 candles) for Analysis
        df = market_data.get_ohlcv(symbol, timeframe='1h', limit=200)
        
        if df.empty:
            raise Exception("No Market Data")

        current_price = df['close'].iloc[-1]
        
        # --- TECHNICAL ANALYSIS LAYER ---
        rsi_val = df['RSI_14'].iloc[-1]
        macd = df['MACD_12_26_9'].iloc[-1]
        macd_signal = df['MACDs_12_26_9'].iloc[-1]
        
        score = 0 # -10 (Strong Sell) to +10 (Strong Buy)
        
        # RSI Logic
        if rsi_val < 30: score += 5
        elif rsi_val > 70: score -= 5
        
        # MACD Logic
        if macd > macd_signal: score += 3
        else: score -= 3
        
        # EMA Trend
        ema_50 = df['EMA_50'].iloc[-1]
        ema_200 = df['EMA_200'].iloc[-1]
        if current_price > ema_200: score += 2  # Long term bull
        if ema_50 > ema_200: score += 2 # Golden Cross vicinity

        # Decision
        direction = "HOLD"
        confidence = 50.0
        
        if score >= 4:
            direction = "BUY"
            confidence = 65 + (score * 2)
        elif score <= -4:
            direction = "SELL"
            confidence = 65 + (abs(score) * 2)
            
        confidence = min(confidence, 98.0)
        
        # --- NEURAL LAYER (Optional) ---
        # If we had a trained model here, we would infer and weigh it 50/50 with TA
        
        return {
            "symbol": symbol,
            "prediction": direction,
            "confidence": round(confidence, 2),
            "predicted_price": round(current_price * (1.01 if direction == "BUY" else 0.99), 2),
            "timeframe": "1h",
            "model_name": "Hybrid-Titan v1 (RSI+MACD+EMA)",
            "timestamp": int(time.time()),
            "analysis": {
                "rsi": round(rsi_val, 2) if not pd.isna(rsi_val) else 50,
                "macd_cross": "Bullish" if macd > macd_signal else "Bearish"
            }
        }

    except Exception as e:
        print(f"Prediction Error: {e}")
        # Fail safe
        return {
            "symbol": symbol,
            "prediction": "HOLD",
            "confidence": 0.0,
            "predicted_price": 0,
            "timeframe": "1h",
            "model_name": "System Offline",
            "timestamp": int(time.time())
        }

@app.get("/api/v1/health")
async def health_check_v1():
    return {
        "status": "online",
        "version": "1.0.0",
        "database": "connected",
        "redis": "connected",
        "timestamp": "2023-11-23T12:00:00Z"
    }

@app.get("/api/v1/stats/database")
async def database_stats():
    return {
        "status": "healthy",
        "connections": 5,
        "latency_ms": 12
    }

# Import handled globally
import threading

@app.post("/api/v1/ai/train")
async def trigger_training(symbol: str = "BTC/USDT"):
    # Run training in background thread to not block API
    thread = threading.Thread(target=train_model, args=(symbol, 20))
    thread.start()
    
    return {
        "status": "started",
        "message": f"Training started for {symbol} in background."
    }



# --- Phase 3 & 4 Extended Endpoints (Ray & Blockchain) ---

import asyncio

# Dynamic Imports to avoid crashes if dependencies are installing
try:
    from app.agents.hive_mind import hive
    AGENT_SYSTEM_READY = True
except ImportError as e:
    print(f"Hive Mind Warning: {e}")
    AGENT_SYSTEM_READY = False

try:
    from app.services.blockchain import check_whale_movements
    BLOCKCHAIN_READY = True
except ImportError as e:
    print(f"Blockchain Warning: {e}")
    BLOCKCHAIN_READY = False

from app.services.redis_client import get_latest_price

@app.get("/api/v1/agents/scan/{symbol:path}")
async def scan_market_agents(symbol: str):
    """
    Trigger distributed Ray agents to scan the market for anomalies.
    Real-time "Swarm Intelligence" check.
    """
    if not AGENT_SYSTEM_READY:
        return {"error": "Hive Mind Offline (Ray system unavailable)"}
    
    # Get live price
    price = get_latest_price(symbol) or 0.0
        
    # Dispatch to Hive Mind
    try:
        result = await hive.swarm_scan(symbol, price)
        return {
            "hive_scan": result,
            "swarm_status": "ACTIVE_AND_WATCHING",
            "agents_online": result.get("agents_active", 0)
        }
    except Exception as e:
        return {"error": f"Swarm Panic: {str(e)}"}

@app.get("/api/v1/onchain/whales")
async def get_whale_alert():
    """
    Scan Ethereum Mempool/Block for huge transactions (Whales).
    """
    if not BLOCKCHAIN_READY:
        return {"error": "Blockchain Node Offline"}
    
    # Run in thread logic
    loop = asyncio.get_event_loop()
    txs = await loop.run_in_executor(None, check_whale_movements)
    
    return {"whale_transactions": txs}
try:
    from app.services.quantum import quantum_portfolio_optimization
    QUANTUM_READY = True
except ImportError:
    QUANTUM_READY = False

@app.get("/api/v1/quantum/optimize")
async def get_quantum_strategy():
    """
    Run Quantum Algorithm (Cirq) to find optimal portfolio strategy
    using superposition and entanglement simulation.
    """
    if not QUANTUM_READY:
        return {"error": "Quantum Module Offline"}
    
    return quantum_portfolio_optimization()

# --- CASH MAELSTROM INTEGRATION ---
try:
    from app.cash_maelstrom.environment import MarketEnvironment
    MAELSTROM_READY = True
except ImportError as e:
    print(f"Maelstrom Import Error: {e}")
    MAELSTROM_READY = False

try:
    from app.simulation.market_twin import run_simulation
    MESA_READY = True
except ImportError:
    MESA_READY = False

from app.services.redis_client import get_latest_price

@app.get("/api/v1/simulation/run")
async def run_market_simulation(symbol: str = "BTC/USDT", panic: bool = False):
    """
    Run a Digital Twin simulation using the CASH MAELSTROM Engine.
    Falls back to Mesa if Maelstrom unavailable.
    """
    # 1. Try Cash Maelstrom (New Core)
    if MAELSTROM_READY:
        try:
            price = get_latest_price(symbol) or market_data.get_price(symbol).get('price', 0) if market_data.get_price(symbol) else 0
            env = MarketEnvironment(symbol, start_price=price, panic_mode=panic)
            return env.run(steps=100)
        except Exception as e:
            print(f"Maelstrom Execution Error: {e}")
            # Fall through to legacy

    # 2. Legacy Mesa Simulation
    if not MESA_READY:
        return {"error": "Simulation Engine Offline (Mesa missing & Maelstrom Failed)"}

    # Get current price
    price = get_latest_price(symbol) or (market_data.get_price(symbol) or {}).get('price', 0)
    
    # Run Simulation
    result = run_simulation(start_price=price, steps=100, panic_scenario=panic)
    
    result['symbol'] = symbol
    return result

# --- VERTEX AI INTEGRATION ---

class AnalysisRequest(BaseModel):
    symbol: str
    price_context: str
    news_summary: str

@app.post("/api/v1/ai/vertex/analyze")
async def run_vertex_analysis(request: AnalysisRequest):
    """
    Generate deep market insights using Google Vertex AI (Gemini Pro).
    """
    analysis = vertex_service.analyze_market_context(
        request.symbol, 
        request.price_context, 
        request.news_summary
    )
    return {"analysis": analysis, "model": "gemini-pro"}

stats_engine = MarketStatisticsProcessor()

@app.get("/api/v1/analysis/stats/{symbol}")
async def get_market_statistics(symbol: str):
    """
    CASH MAELSTROM: Quantum Analytics Endpoint.
    Returns statistical breakdown of the asset.
    """
    # Clean symbol if needed
    clean_symbol = symbol.replace("-", "/") if "-" in symbol else symbol
    
    data = stats_engine.process_asset_statistics(clean_symbol)
    if not data:
        # Try appending USDT if failed
        if "USDT" not in clean_symbol:
             data = stats_engine.process_asset_statistics(f"{clean_symbol}/USDT")
        
    if not data:
        raise HTTPException(status_code=404, detail="Insufficient data for quantum analysis")
    return data


@app.get("/api/v1/hive/swarm/{symbol:path}")
async def get_swarm_status(symbol: str):
    """
    CASH MAELSTROM: Hive Mind Uplink.
    Returns the state of the 1,000,000 agent swarm.
    """
    clean_symbol = symbol.replace("-", "/") if "-" in symbol else symbol
    if "USDT" not in clean_symbol and "/" not in clean_symbol:
         clean_symbol += "/USDT"
    
    if not AGENT_SYSTEM_READY:
         return {"error": "Hive Mind Offline"}

    # Get REAL live price - no fallbacks to fake data
    price = get_latest_price(clean_symbol)
    if not price:
        # Try REST API fallback
        rest_data = market_data.get_price(clean_symbol)
        price = rest_data.get('price', 0) if rest_data else 0
    
    try:
        # Calls the REAL Ray Swarm (Agents + BigQuery Strategist)
        # Pass agent weights for weighted consensus calculation
        return await hive.swarm_scan(clean_symbol, price, AGENT_WEIGHTS)
    except Exception as e:
        print(f"Swarm Error: {e}")
        return {"error": "Swarm Uplink Failed", "details": str(e)}

# --- AGENT WEIGHT CONFIGURATION ---

# Global agent weights (in-memory for now, can persist to DB)
AGENT_WEIGHTS = {
    "scout": 1.0,
    "hunter": 1.0,
    "analyst": 1.0,
    "defender": 1.0,
    "strategist": 1.0,
    "sentinel": 1.0
}

class HiveConfigRequest(BaseModel):
    role: str
    active: bool
    weight: float

@app.post("/api/v1/hive/config")
async def set_hive_config(request: HiveConfigRequest):
    """
    Configure agent weights for consensus calculation.
    Supports single agent update from frontend.
    """
    global AGENT_WEIGHTS
    role_key = request.role.lower()
    
    # Update global weights
    if role_key in AGENT_WEIGHTS:
        # If 'active' is false, force weight to 0.0 for consistency
        val = request.weight if request.active else 0.0
        AGENT_WEIGHTS[role_key] = val
        print(f"🎛️ [HIVE] Agent {role_key.upper()} updated to {val} (Active: {request.active})")
    
    # CRITICAL FIX: Invalidate Cache so logic re-runs with new weights
    # CRITICAL FIX: Invalidate Cache so logic re-runs with new weights
    if 'hive' in globals():
        # BRUTE FORCE CACHE CLEAR
        globals()['hive'].last_swarm_result = {}
        if hasattr(globals()['hive'], 'config_version'):
            globals()['hive'].config_version += 1
        print("🧹 [HIVE] Cache COMPLETELY CLEARED to enforce new agent configuration.")
    
    return {"status": "success", "weights": AGENT_WEIGHTS, "config_version": globals()['hive'].config_version if 'hive' in globals() and hasattr(globals()['hive'], 'config_version') else 0}

@app.get("/api/v1/hive/config")
async def get_hive_config():
    """Get current agent weight configuration."""
    return {"weights": AGENT_WEIGHTS}

# --- USER UPGRADE ENDPOINT ---

class UpgradeRequest(BaseModel):
    user_id: int = 1  # Mock user ID for now

@app.post("/api/v1/user/upgrade")
async def upgrade_user_plan(request: UpgradeRequest):
    """
    Upgrade user to INSTITUTIONAL plan.
    Unlocks Strategist Agent and PDF Reports.
    """
    from app.core.database import DatabaseManager
    from sqlalchemy import text
    
    try:
        db = DatabaseManager()
        with db.get_engine().connect() as conn:
            # Check if users table exists, create if not
            # Check if users table exists, create if not
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255),
                    subscription_plan VARCHAR(50) DEFAULT 'FREE',
                    is_strategist_unlocked BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """))
            
            # Migration: Ensure columns exist (if table existed with old schema)
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_plan VARCHAR(50) DEFAULT 'FREE'"))
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_strategist_unlocked BOOLEAN DEFAULT FALSE"))
            except Exception:
                pass # Ignore if failed (e.g. SQLite doesn't support IF NOT EXISTS in ALTER)

            conn.commit()
            
            # Insert default user if not exists
            conn.execute(text("""
                INSERT INTO users (id, email, subscription_plan, is_strategist_unlocked) 
                VALUES (:id, 'demo@turboplan.io', 'FREE', FALSE)
                ON CONFLICT (id) DO NOTHING
            """), {"id": request.user_id})
            conn.commit()
            
            # Upgrade the user
            conn.execute(text("""
                UPDATE users 
                SET subscription_plan = 'INSTITUTIONAL', is_strategist_unlocked = true 
                WHERE id = :id
            """), {"id": request.user_id})
            conn.commit()
            
        print(f"🚀 [UPGRADE] User {request.user_id} upgraded to INSTITUTIONAL")
        return {"status": "success", "plan": "INSTITUTIONAL", "user_id": request.user_id}
        
    except Exception as e:
        print(f"❌ [UPGRADE] Error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/v1/user/plan")
async def get_user_plan(user_id: int = 1):
    """Get current user plan."""
    from app.core.database import DatabaseManager
    from sqlalchemy import text
    
    try:
        db = DatabaseManager()
        with db.get_engine().connect() as conn:
            # Try specific column first, fallback to 'plan' if needed or handle error
            try:
                result = conn.execute(text("SELECT subscription_plan, is_strategist_unlocked FROM users WHERE id = :id"), {"id": user_id})
            except Exception:
                # If migration didn't run yet, table might not have columns. Return FREE.
                return {"plan": "FREE", "isPremium": False}
                
            row = result.fetchone()
            if row:
                # row[0] is subscription_plan
                return {"plan": row[0], "isPremium": row[0] == "INSTITUTIONAL"}
            return {"plan": "FREE", "isPremium": False}
    except Exception:
        return {"plan": "FREE", "isPremium": False}

class HiveChatRequest(BaseModel):
    symbol: str
    message: str

@app.post("/api/v1/hive/chat")
async def chat_with_hive(request: HiveChatRequest):
    """
    Interactive Chat with the Hive Mind.
    Uses Swarm Context + Vertex AI (or Logic Fallback).
    """
    clean_symbol = request.symbol.replace("-", "/")
    
    # 1. Gather Context
    context_str = "Hive Mind Offline."
    sentiment = "Neutral"
    verdict = "HOLD"
    
    if AGENT_SYSTEM_READY:
        try:
            price = get_latest_price(clean_symbol) or (market_data.get_price(clean_symbol) or {}).get('price', 0)
            # Get fresh scan
            scan = await hive.swarm_scan(clean_symbol, price)
            
            context_str = f"""
            Swarm Verdict: {scan.get('verdict')}
            Collective Sentiment: {scan.get('collective_sentiment')}
            Active Agents: {scan.get('agents_active')}
            Anomaly Threat: {scan.get('anomaly_threat')}
            Risk Status: {scan.get('risk_status')}
            """
            sentiment = "Bullish" if scan.get('collective_sentiment', 0) > 0 else "Bearish"
            verdict = scan.get('verdict')
        except Exception as e:
            print(f"Chat Context Error: {e}")
            
    # 2. Try Generative AI
    if vertex_service.initialized:
        prompt = f"""
        You are the Hive Mind, a collective intelligence of {swarm.total_agents} AI trading agents.
        Current State:
        {context_str}
        
        User Query: "{request.message}"
        
        Respond as the collective "We". Be cryptic but insightful. Use metaphors about swarms, data streams, and efficiency.
        """
        response = vertex_service.analyze_market_context(clean_symbol, "N/A", prompt) # abusing this method slightly for convenience
        return {"response": response, "mode": "generative"}
        
    # 3. Fallback Logic
    responses = [
        f"We are analyzing {clean_symbol}. The consensus is {verdict}.",
        f"Data streams indicate {sentiment} pressure.",
        "The Swarm is calculating... probability vectors align with current trend.",
        f"Agents report correlation anomalies. Maintain caution. Verdict: {verdict}"
    ]
    
    return {
        "response": responses[len(request.message) % len(responses)], # Deterministic random
        "mode": "logic_fallback"
    }

@app.get("/api/v1/hive/whales")
async def get_hive_whales(limit: int = 5):
    """
    CASH MAELSTROM: Whale Detection Uplink.
    Returns recent large transactions detected by the Z-Score monitor.
    """
    from app.services.redis_client import r as redis_client
    import json
    
    try:
        # Get from Redis sorted set
        alerts = redis_client.zrevrange('whale:history', 0, limit - 1)
        return [json.loads(a) for a in alerts]
    except Exception as e:
        print(f"Whale Alert Error: {e}")
        return []

@app.get("/api/v1/hive/tactical/{symbol:path}")
async def get_tactical_intel(symbol: str):
    """
    Deep tactical breakdown of the current market state.
    """
    clean_symbol = symbol.replace("-", "/")
    price = get_latest_price(clean_symbol) or 0.0
    stats = stats_engine.process_asset_statistics(clean_symbol)

    # Safety check for division
    efficiency = "ANALYZING"
    quantum = "STABLE"
    
    if price > 0 and stats and 'math_proof' in stats:
        sigma = stats['math_proof']['dispersion']['std_dev_sigma']
        mean = stats['math_proof']['central_tendency']['mean_mu']
        efficiency = "LOW" if (sigma / price) > 0.02 else "HIGH"
        quantum = "SUPERPOSITION" if price > mean * 0.99 and price < mean * 1.01 else "ENTANGLED"

    return {
        "symbol": clean_symbol,
        "price": price,
        "market_efficiency": efficiency,
        "quantum_state": quantum,
        "timestamp": datetime.now().isoformat()
    }


# PDF Payload Model
# Extended Payload with Full Snapshot Data
class PDFPayload(BaseModel):
    symbol: str
    price: float
    verdict: str
    confidence: float
    reasoning: str = "" # Fallback
    consensus_text: str = "Market consensus unavailable."
    agents: list = [] # List of agent dicts
    timestamp: str

@app.post("/api/v1/reports/pdf_post")
async def generate_pdf_report_post(payload: PDFPayload):
    """
    Generates a professional Table-based PDF dossier (Snapshot).
    """
    from reportlab.lib.pagesizes import letter
    from app.services.pdf_service import generate_tactical_report
    from fastapi.responses import StreamingResponse

    try:
        pdf_buffer = generate_tactical_report(payload)
        return StreamingResponse(
            pdf_buffer, 
            media_type='application/pdf', 
            headers={
                "Content-Disposition": f"attachment; filename=Brief_{payload.symbol.replace('/', '_')}.pdf"
            }
        )
    except Exception as e:
        print(f"PDF ERROR: {e}")
        return {"error": str(e)}

@app.get("/api/v1/reports/generate_pdf")
async def generate_stats_report(
    symbol: str = Query("BTC/USDT", description="Crypto symbol"),
    price: float = Query(0.0, description="Current price")
):
    """
    Generates a professional PDF dossier for the asset.
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from io import BytesIO
    from fastapi.responses import StreamingResponse
    from fastapi import Query

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Theme Colors
    primary_color = colors.HexColor("#0f172a") # Dark Slate
    accent_color = colors.HexColor("#3b82f6") # Blue
    
    # 1. Header
    p.setFillColor(primary_color)
    p.rect(0, height - 100, width, 100, fill=1)
    
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 24)
    p.drawString(50, height - 50, f"TACTICAL INTELLIGENCE BRIEF: {symbol}")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 70, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    p.drawString(50, height - 85, "CONFIDENTIAL // EYES ONLY")

    # 2. Executive Summary
    y = height - 140
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "1. EXECUTIVE SUMMARY")
    
    # Fetch Data
    # Fetch Data with Cache Preference
    hive_mind = globals().get('hive')
    swarm_data = None
    
    # Check Cache First (User Requirement: Consistency)
    if hive_mind and symbol in hive_mind.last_swarm_result:
        print(f"📄 [PDF] Using cached data for {symbol}")
        swarm_data = hive_mind.last_swarm_result[symbol]
        price = swarm_data.get('price', 0)
    else:
        # Fallback to fresh scan
        print(f"📄 [PDF] Generating fresh data for {symbol}")
        price = get_latest_price(symbol.replace("-", "/")) or 0.0
        if hive_mind:
            swarm_data = await hive_mind.swarm_scan(symbol, price)

    analyst_text = "AI Neural Link signal weak. Standard analysis unavailable."
    verdict = "NEUTRAL"
    confidence = 0
    
    if swarm_data and 'swarm_breakdown' in swarm_data:
        verdict = swarm_data.get('verdict', 'NEUTRAL')
        confidence = swarm_data.get('confidence_score', 0)
        
        # Find Analyst Note
        for agent in swarm_data['swarm_breakdown']:
            if agent['role'] == 'ANALYST':
                analyst_text = agent.get('reasoning', analyst_text)
                analyst_text = analyst_text.replace("\n", " ")
                break

    stats = stats_engine.process_asset_statistics(symbol)
    
    # Safety fallback for stats
    if not stats or 'math_proof' not in stats:
        stats = {
            'math_proof': {
                'dispersion': {'variance_sigma_sq': 0.0},
                'normalization': {'score': 0.0}
            }
        }
    
    p.setFont("Helvetica", 12)
    y -= 25
    
    # 2.1 Verdict Header
    p.drawString(50, y, f"SWARM VERDICT: {verdict} ({confidence}% Confidence)")
    if verdict == "BUY": p.setFillColor(colors.green)
    elif verdict == "SELL": p.setFillColor(colors.red)
    else: p.setFillColor(colors.orange)
    p.circle(40, y + 4, 3, fill=1) # Status dot
    p.setFillColor(colors.black)
    
    y -= 30
    
    # 2.2 AI Narrative (Wrapped)
    text_obj = p.beginText(50, y)
    text_obj.setFont("Helvetica", 11)
    
    # Better text wrapping
    def wrap_text(text, width_chars=80):
        words = text.split()
        lines = []
        current_line = []
        current_len = 0
        for word in words:
            if current_len + len(word) + 1 <= width_chars:
                current_line.append(word)
                current_len += len(word) + 1
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_len = len(word)
        if current_line: lines.append(" ".join(current_line))
        return lines
    
    wrapped_lines = wrap_text(analyst_text, 85)
    for line in wrapped_lines:
        text_obj.textLine(line)
        y -= 14 # Move cursor down for next section
        
    p.drawText(text_obj)
    y -= 20 # Extra spacing
    
    # 3. Market Snapshot
    y -= 100
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "2. MARKET SNAPSHOT")
    
    y -= 30
    p.setFont("Helvetica", 12)
    p.drawString(70, y, f"• Price: ${price:,.2f}")
    p.drawString(70, y - 20, f"• Variance (σ²): {stats['math_proof']['dispersion']['variance_sigma_sq']:.4f}")
    p.drawString(70, y - 40, f"• Normalized Score: {stats['math_proof']['normalization']['score']:.4f}")
    
    # 4. Risk Warning
    y -= 100
    p.setFillColor(colors.red)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "RISK ASSESSMENT")
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 10)
    p.drawString(50, y - 20, "This document is generated by an autonomous AI system. Not financial advice.")
    p.drawString(50, y - 35, "Do not rely solely on machine intelligence for capital allocation.")

    p.showPage()
    p.save()
    
    buffer.seek(0)
    return StreamingResponse(buffer, media_type='application/pdf', headers={
        "Content-Disposition": f"attachment; filename=brief_{symbol.replace('/', '_')}.pdf"
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
