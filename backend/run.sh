#!/bin/bash
# TURBO-PLAN X - Backend Server Launcher

set -e

echo "======================================"
echo "TURBO-PLAN X - Backend API Server"
echo "======================================"
echo ""

cd "$(dirname "$0")"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Check infrastructure
echo "Checking infrastructure..."
if ! docker ps | grep -q turboplanx-timescaledb; then
    echo "❌ TimescaleDB is not running!"
    echo "Start it with: docker start turboplanx-timescaledb"
    exit 1
fi

if ! docker ps | grep -q turboplanx-redis; then
    echo "❌ Redis is not running!"
    echo "Start it with: docker start turboplanx-redis"
    exit 1
fi

echo "✓ TimescaleDB running"
echo "✓ Redis running"
echo ""

echo "Starting FastAPI server..."
echo "======================================"
echo "API Docs: http://localhost:8000/docs"
echo "Health: http://localhost:8000/api/v1/health"
echo "WebSocket: ws://localhost:8000/ws/market"
echo "======================================"
echo ""

# Start server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
