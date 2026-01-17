# TURBO-PLAN X - Data Pipeline

Professional cryptocurrency data pipeline for TURBO-PLAN X AI Hedge Fund.

## ✅ What's Currently Working

### Infrastructure (100% Ready)
- ✅ **TimescaleDB** - Running on port 5432
  - 5 hypertables configured (ohlcv, trades, orderbook, ai_signals, agent_logs)
  - Compression enabled (90% storage savings)
  - Materialized views for performance
  - PostgreSQL 16.11 + TimescaleDB 2.24.0

- ✅ **Redis** - Running on port 6379
  - Caching layer for real-time data
  - Pub/Sub for WebSocket streams

### Python Environment (100% Ready)
- ✅ Virtual environment created
- ✅ All dependencies installed:
  - ccxt 4.2.25 (exchange API)
  - psycopg2 (PostgreSQL driver)
  - redis, pandas, numpy
  - loguru (logging)

### Code Components (100% Ready)
- ✅ `database.py` - Professional DB manager with connection pooling
- ✅ `fetch_historical.py` - Historical data fetcher with rate limiting
- ✅ `fetch_historical.sh` - Quick start script

---

## 🚀 Quick Start

### 1. Check Infrastructure Status

```bash
# Check if Docker containers are running
docker ps

# Should see:
# - turboplanx-timescaledb (port 5432)
# - turboplanx-redis (port 6379)
```

### 2. Fetch Historical Data (First Time Setup)

```bash
cd data_pipeline
./fetch_historical.sh
```

This will:
- Fetch 1 year of historical data
- For 10 major cryptocurrencies (BTC, ETH, SOL, etc.)
- In 3 timeframes (1h, 4h, 1d)
- Store in TimescaleDB
- Takes ~10-30 minutes

### 3. Verify Data

```bash
# Connect to database
docker exec -it turboplanx-timescaledb psql -U postgres -d turboplanx

# Check data
SELECT symbol, timeframe, COUNT(*) as candles 
FROM ohlcv 
GROUP BY symbol, timeframe 
ORDER BY symbol, timeframe;
```

---

## 📁 File Structure

```
data_pipeline/
├── venv/                   # Python virtual environment
├── docker-compose.yml      # Docker services config
├── init_db.sql            # Database schema
├── requirements.txt       # Python dependencies
├── database.py            # DB connection manager ✅
├── fetch_historical.py    # Historical data fetcher ✅
├── fetch_historical.sh    # Quick start script ✅
└── README.md             # This file
```

---

## 🔧 Configuration

All configuration is in the root `.env` file:

```bash
# Database
POSTGRES_PASSWORD=turboplanx_secure_password
POSTGRES_DB=turboplanx
DATABASE_URL=postgresql://postgres:turboplanx_secure_password@localhost:5432/turboplanx

# Redis
REDIS_URL=redis://localhost:6379

# Exchange APIs (optional for public data)
BINANCE_API_KEY=your_key_here
BINANCE_SECRET=your_secret_here
```

---

## 📊 Database Schema

### Main Tables

1. **ohlcv** - OHLCV candlestick data (hypertable)
   - Columns: time, symbol, timeframe, open, high, low, close, volume
   - Indexes: symbol+time, symbol+timeframe+time
   - Compression: Enabled (7 day policy)

2. **trades** - Individual trades (hypertable)
   - Real-time trade execution data
   - Compression: 3 day policy

3. **orderbook_snapshots** - Order book depth (hypertable)
   - Bids/asks arrays in JSONB

4. **ai_signals** - AI predictions and signals (hypertable)
   - Model outputs, confidence scores

5. **agent_logs** - AI agent activity (hypertable)
   - Scout, analyst, hunter, defender logs

---

## 🛠 Development Tools

### Test Database Connection

```bash
cd data_pipeline
source venv/bin/activate
python database.py
```

Expected output:
```
✓ PostgreSQL connected
✓ TimescaleDB version: 2.24.0
✓ Redis connected
```

### Stop/Start Infrastructure

```bash
# Stop containers
docker stop turboplanx-timescaledb turboplanx-redis

# Start containers
docker start turboplanx-timescaledb turboplanx-redis

# View logs
docker logs turboplanx-timescaledb
docker logs turboplanx-redis
```

---

## 📈 Next Steps

### Immediate (Not Yet Started)
- [ ] Real-time WebSocket streamer
- [ ] FastAPI backend  
- [ ] Frontend integration

### Coming Soon
- [ ] AI model training pipeline
- [ ] Ray agent orchestration
- [ ] MEV detection
- [ ] Whale profiling

---

## 💡 Tips

1. **First time?** Run `./fetch_historical.sh` to populate the database
2. **Rate limits?** The fetcher has automatic rate limiting built-in
3. **Low on disk?** TimescaleDB compression saves 90% space automatically
4. **Need more data?** Edit `fetch_historical.py` to add more symbols/timeframes

---

## ⚠️ Troubleshooting

### Port 5432 already in use
```bash
# Check what's using it
sudo lsof -i :5432

# Stop old container if needed
docker stop turbo_timescale
docker rm turbo_timescale
```

### Database connection failed
```bash
# Check container status
docker ps
docker logs turboplanx-timescaledb

# Restart if needed
docker restart turboplanx-timescaledb
```

---

**Status**: ✅ Phase 2 Infrastructure - COMPLETE  
**Next Phase**: Real-time data streaming + FastAPI backend
