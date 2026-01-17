# TURBO-PLAN X - Backend API

Professional FastAPI backend for the TURBO-PLAN X AI Hedge Fund platform.

## 🚀 Quick Start

```bash
cd backend
./run.sh
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health**: http://localhost:8000/api/v1/health
- **WebSocket**: ws://localhost:8000/ws/market

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── core/
│   │   ├── config.py          # Configuration
│   │   └── database.py        # Database manager
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── services/              # Business logic (future)
│   └── main.py                # FastAPI app
├── requirements.txt           # Python dependencies
└── run.sh                     # Launch script
```

## 🔌 API Endpoints

### Market Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/market/ticker/{symbol}` | Real-time ticker |
| GET | `/api/v1/market/ohlcv/{symbol}` | Historical OHLCV |
| GET | `/api/v1/market/orderbook/{symbol}` | Order book depth |

### AI

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/ai/prediction/{symbol}` | AI prediction (mock) |
| GET | `/api/v1/ai/agents/status` | Hive-Mind status (mock) |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/stats/database` | Database statistics |
| WS | `/ws/market` | Real-time WebSocket |

## 🧪 Testing

### Test Ticker Endpoint
```bash
curl http://localhost:8000/api/v1/market/ticker/BTC/USDT
```

### Test Historical Data
```bash
curl "http://localhost:8000/api/v1/market/ohlcv/BTC/USDT?timeframe=1h&limit=10"
```

### Test WebSocket
```bash
# Install websocat: cargo install websocat
websocat ws://localhost:8000/ws/market
```

## ⚙️ Configuration

Configuration is managed via environment variables (`.env` file in project root):

```bash
# Database
DATABASE_URL=postgresql://postgres:turboplanx_secure_password@localhost:5432/turboplanx

# Redis
REDIS_URL=redis://localhost:6379

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

## 📊 Response Examples

### Ticker Response
```json
{
  "symbol": "BTC/USDT",
  "last": 89271.39,
  "bid": 89271.39,
  "ask": 89271.4,
  "high": 90588.23,
  "low": 88123.45,
  "volume": 1234567.89,
  "change_24h": 1.23,
  "timestamp": 1703254800000
}
```

### OHLCV Response
```json
{
  "symbol": "BTC/USDT",
  "timeframe": "1h",
  "candles": [
    {
      "time": 1703254800000,
      "open": 89000.0,
      "high": 89500.0,
      "low": 88800.0,
      "close": 89271.39,
      "volume": 123.45
    }
  ],
  "count": 1
}
```

## 🔒 CORS

CORS is enabled for:
- http://localhost:3000 (Frontend)
- http://localhost:3001 (Alternative)

## 📝 Development

### Install dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run in development mode
```bash
uvicorn app.main:app --reload
```

### Run tests (future)
```bash
pytest
```

## 🐛 Troubleshooting

### Port 8000 already in use
```bash
# Find process
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database connection failed
```bash
# Check if Docker containers are running
docker ps

# Start if needed
docker start turboplanx-timescaledb
docker start turboplanx-redis
```

## 🚀 Deployment (Future)

- Docker containerization
- Google Cloud Run deployment
- Kubernetes manifests
- CI/CD with GitHub Actions

---

**Status**: ✅ Fully functional backend API
**Next**: Integrate with frontend
