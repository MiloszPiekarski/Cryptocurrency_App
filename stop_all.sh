#!/bin/bash
# TURBO-PLAN X - Stop All Services

echo "═══════════════════════════════════════════════"
echo "   🛑 TURBO-PLAN X - Stopping All Services"
echo "═══════════════════════════════════════════════"
echo ""

# Stop Frontend
echo "🎨 Stopping Frontend..."
pkill -f "next dev" && echo "   ✓ Frontend stopped" || echo "   ℹ️  Frontend not running"

# Stop Backend
echo "🔧 Stopping Backend..."
pkill -f "uvicorn.*main:app" && echo "   ✓ Backend stopped" || echo "   ℹ️  Backend not running"

# Stop Streamer
echo "📡 Stopping Data Streamer..."
pkill -f "stream_realtime.py" && echo "   ✓ Streamer stopped" || echo "   ℹ️  Streamer not running"

# Stop Docker (optional - comment out if you want to keep DB running)
echo "📦 Stopping Docker containers..."
cd "$(dirname "${BASH_SOURCE[0]}")/data_pipeline"
docker-compose down && echo "   ✓ Docker stopped" || echo "   ℹ️  Docker not running"

echo ""
echo "✅ All services stopped!"
echo ""
