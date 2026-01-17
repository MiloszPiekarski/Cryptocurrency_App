#!/bin/bash
# TURBO-PLAN X - Complete Startup Script
# Uruchamia wszystkie komponenty systemu

set -e

echo "═══════════════════════════════════════════════"
echo "   🚀 TURBO-PLAN X - Starting All Services"
echo "═══════════════════════════════════════════════"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Start Docker (Database + Redis)
echo "📦 Step 1/4: Starting Docker containers..."
cd data_pipeline
if docker ps | grep -q turboplanx-timescaledb; then
    echo "   ✓ Docker already running"
else
    docker-compose up -d
    echo "   ✓ Docker started, waiting for initialization..."
    sleep 5
fi
cd ..

# 2. Start Real-time Data Streamer
echo ""
echo "📡 Step 2/4: Starting Real-time Data Streamer..."
cd data_pipeline
if ps aux | grep -v grep | grep -q "python stream_realtime.py"; then
    echo "   ✓ Streamer already running"
else
    source venv/bin/activate
    nohup python stream_realtime.py > /tmp/streamer.log 2>&1 &
    echo "   ✓ Streamer started (PID: $!)"
    deactivate
fi
cd ..

# 3. Start Backend API
echo ""
echo "🔧 Step 3/4: Starting Backend API..."
cd backend
if ps aux | grep -v grep | grep -q "uvicorn.*main:app"; then
    echo "   ✓ Backend already running"
else
    source venv/bin/activate
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
    echo "   ✓ Backend started (PID: $!)"
    deactivate
fi
cd ..

# 4. Start Frontend
echo ""
echo "🎨 Step 4/4: Starting Frontend..."
cd web_app/frontend
if ps aux | grep -v grep | grep -q "next dev"; then
    echo "   ✓ Frontend already running"
else
    nohup npm run dev > /tmp/frontend.log 2>&1 &
    echo "   ✓ Frontend started (PID: $!)"
fi
cd ../..

# Wait a moment for services to initialize
echo ""
echo "⏳ Waiting for services to initialize..."
sleep 8

# Verify all services
echo ""
echo "═══════════════════════════════════════════════"
echo "   ✅ Checking Service Status"
echo "═══════════════════════════════════════════════"

# Check Docker
if docker ps | grep -q turboplanx-timescaledb; then
    echo "✅ Docker:     Running"
else
    echo "❌ Docker:     Not running"
fi

# Check Streamer
if ps aux | grep -v grep | grep -q "python stream_realtime.py"; then
    echo "✅ Streamer:   Running"
else
    echo "❌ Streamer:   Not running"
fi

# Check Backend
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "✅ Backend:    Running on http://localhost:8000"
else
    echo "❌ Backend:    Not responding"
fi

# Check Frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend:   Running on http://localhost:3000"
else
    echo "⏳ Frontend:   Starting... (may take 10-20 seconds)"
fi

echo ""
echo "═══════════════════════════════════════════════"
echo "   🎉 All Services Started!"
echo "═══════════════════════════════════════════════"
echo ""
echo "📍 URLs:"
echo "   Frontend:  http://localhost:3000"
echo "   Dashboard: http://localhost:3000/dashboard"
echo "   Charts:    http://localhost:3000/charts"
echo "   Backend:   http://localhost:8000/docs"
echo ""
echo "📋 Logs:"
echo "   Streamer:  tail -f /tmp/streamer.log"
echo "   Backend:   tail -f /tmp/backend.log"
echo "   Frontend:  tail -f /tmp/frontend.log"
echo ""
echo "🛑 To stop all services, run: ./stop_all.sh"
echo ""
