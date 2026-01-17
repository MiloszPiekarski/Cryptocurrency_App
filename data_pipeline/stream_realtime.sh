#!/bin/bash
# TURBO-PLAN X - Real-Time Streamer Launcher
# Starts the real-time market data streamer

set -e

echo "======================================"
echo "TURBO-PLAN X - Real-Time Streamer"
echo "======================================"
echo ""

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

echo "✓ Virtual environment activated"
echo ""

# Check if database is running
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

echo "Starting real-time market data streamer..."
echo "This will:"
echo "  - Stream live prices to Redis"
echo "  - Update order books"
echo "  - Save 1-minute candles to database"
echo ""
echo "Press Ctrl+C to stop"
echo "======================================"
echo ""

python stream_realtime.py
