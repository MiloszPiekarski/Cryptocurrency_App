#!/bin/bash
# TURBO-PLAN X - Quick Start Script
# Fetches initial historical data (1 year for top 10 coins)

set -e

echo "======================================"
echo "TURBO-PLAN X - Historical Data Fetch"
echo "======================================"
echo ""

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

echo "✓ Virtual environment activated"
echo ""

# Run fetcher
echo "Starting historical data fetch..."
echo "This will fetch 1 year of data for 10 major cryptocurrencies"
echo "Estimated time: 10-30 minutes depending on connection"
echo ""

python fetch_historical.py

echo ""
echo "======================================"
echo "✓ Historical data fetch complete!"
echo "======================================"
