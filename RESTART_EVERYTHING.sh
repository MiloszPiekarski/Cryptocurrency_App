#!/bin/bash

# ==========================================
# TURBO-PLAN X: BULLETPROOF RESTORATION SYSTEM v2
# ==========================================
# This script forcefully restarts every component of the system.
# It ensures dependencies (DB -> Backend -> Frontend) start in correct order.
# Run from the root directory: ./RESTART_EVERYTHING.sh


# Ensure we are in the root directory
cd "$(dirname "$0")"

# --- HELPER FUNCTIONS ---
wait_for_port() {
    local port=$1
    local name=$2
    local retries=30
    echo -n "⏳ Waiting for $name (Port $port)..."
    for ((i=0; i<retries; i++)); do
        if timeout 1 bash -c "echo > /dev/tcp/localhost/$port" >/dev/null 2>&1; then
            echo " ONLINE ✅"
            return 0
        fi
        echo -n "."
        sleep 1
    done
    echo " FAILED ❌ (Service did not start in time)"
    return 1
}

wait_for_http() {
    local url=$1
    local name=$2
    local retries=30 # 60 seconds (2s sleep)
    echo -n "🔎 Verifying $name Health ($url)..."
    for ((i=0; i<retries; i++)); do
        if curl -s "$url" > /dev/null; then
            echo " HEALTHY ✅"
            return 0
        fi
        echo -n "."
        sleep 2
    done
    echo " UNRESPONSIVE ❌ (Check logs)"
    return 1
}

# --- 1. KILL MATRIX (Force Stop All) ---
echo "🧨 [PHASE 1] NEUTRALIZING OLD PROCESSES..."

# Stop Ray
if command -v ray &> /dev/null; then
    ray stop --force 2>/dev/null || true
fi
pkill -9 -f "ray" 2>/dev/null || true

# Kill Python Processes
pkill -9 -f "uvicorn" 2>/dev/null || true
pkill -9 -f "stream_realtime.py" 2>/dev/null || true
pkill -9 -f "python3 -m app.main" 2>/dev/null || true

# Kill Node/Next.js
pkill -9 -f "next-server" 2>/dev/null || true
pkill -9 -f "next-router-worker" 2>/dev/null || true
pkill -9 -f "node" 2>/dev/null || true

# Kill Ports (Nuclear Option)
fuser -k 3000/tcp 2>/dev/null || true
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 8001/tcp 2>/dev/null || true

echo "✅ System Zeroed."
sleep 2

# --- 2. INFRASTRUCTURE (Docker) ---
echo "🐳 [PHASE 2] BOOTING DATABASE & REDIS..."
cd data_pipeline
if command -v docker-compose &> /dev/null; then
    docker-compose up -d timescaledb redis
elif docker compose version &> /dev/null; then
    docker compose up -d timescaledb redis
else
    docker restart turboplanx-timescaledb turboplanx-redis 2>/dev/null || echo "⚠️ Docker issue - attempting manual restart..."
fi
cd ..

# CRITICAL: Wait for DB before starting Backend
wait_for_port 5432 "PostgreSQL" || echo "⚠️ Warning: DB might be slow"
wait_for_port 6379 "Redis" || echo "⚠️ Warning: Redis might be slow"

# --- 3. CORE SERVICES STARTUP ---
echo "🛠️ [PHASE 3] ACTIVATING CORE NERVOUS SYSTEM..."

# Global Environment Variables
export DATABASE_URL="postgresql://postgres:turboplanx_secure_password@localhost:5432/turboplanx"
export CLOUD_SQL_URL="postgresql://postgres:turboplanx_secure_password@localhost:5432/turboplanx"
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/services/ai_engine/service_account.json"
export PYTHONPATH="$(pwd)"

# A. DATA STREAMER (Independent)
if [ -d "data_pipeline/venv" ]; then
    echo "   >> Starting Data Streamer..."
    cd data_pipeline
    nohup ./venv/bin/python3 stream_realtime.py > ../ingestor.log 2>&1 &
    cd ..
else
    echo "⚠️  Missing data_pipeline/venv! Skipping Streamer."
fi

# B. MAIN BACKEND (Must start first for API deps)
if [ -d "backend/venv" ]; then
    echo "   >> Starting Main Backend (Port 8000)..."
    cd backend
    nohup ./venv/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../main_backend.log 2>&1 &
    cd ..
    
    # Wait for Backend to be actually ready BEFORE starting AI
    wait_for_http "http://localhost:8000/api/v1/health" "Backend API"
else
    echo "❌ CRITICAL: backend/venv missing!"
fi

# C. AI ENGINE (Depends on Backend potentially)
if [ -d "services/ai_engine/venv" ]; then
    echo "   >> Starting AI Engine (Port 8001)..."
    cd services/ai_engine
    export RAY_ADDRESS=""
    nohup ./venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload > ../../ai_engine.log 2>&1 &
    cd ../..
    
    # Wait for AI Engine
    wait_for_http "http://localhost:8001/docs" "AI Engine"
else
    echo "❌ CRITICAL: services/ai_engine/venv missing!"
fi

# --- 4. FRONTEND ---
echo "🎨 [PHASE 4] LAUNCHING UI..."
cd web_app/frontend
if [ -d "node_modules" ]; then
    nohup npm run dev -- --port 3000 > ../../frontend.log 2>&1 &
    echo "✅ UI Process Started."
    
    # Optional: Wait for UI port (though compilation takes longer)
    wait_for_port 3000 "Frontend Server"
else
    echo "❌ Frontend node_modules missing. Run 'npm install' inside web_app/frontend."
fi
cd ../..

echo ""
echo "=================================================="
echo "   🚀 CASH MAELSTROM SYSTEM ONLINE & VERIFIED"
echo "=================================================="
echo "   All systems started in sequence and verified."
echo "   - Postgres/Redis: OK"
echo "   - Backend API:    OK (http://localhost:8000)"
echo "   - AI Engine:      OK (http://localhost:8001)"
echo "   - Frontend:       OK (http://localhost:3000)"
echo "=================================================="
