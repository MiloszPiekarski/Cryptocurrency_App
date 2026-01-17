-- TURBO-PLAN X: Market Data Database Schema
-- Optimized for High-Frequency Access (2026 Standards)

-- Enable TimescaleDB extension for time-series optimization
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- TABLE: market_history ("Hot Storage")
-- Stores granular market data for the last 48 hours.
-- Older data is archived to BigQuery via ETL.
CREATE TABLE IF NOT EXISTS market_history (
    time        TIMESTAMPTZ NOT NULL,
    symbol      TEXT NOT NULL,
    price       DOUBLE PRECISION NOT NULL,
    volume      DOUBLE PRECISION,
    source      TEXT DEFAULT 'exchanges',
    
    -- Composite primary key (time + symbol) for TimescaleDB
    PRIMARY KEY (time, symbol)
);

-- Convert to Hypertables (TimescaleDB magic)
-- Partitions data by time chunks (e.g., 1 day) for instant query speed
SELECT create_hypertable('market_history', 'time', if_not_exists => TRUE);

-- INDICES (Crucial for performance)
-- 1. Asset Pair Lookup (e.g., WHERE symbol = 'BTC/USDT')
CREATE INDEX IF NOT EXISTS idx_market_symbol ON market_history (symbol, time DESC);

-- 2. Time-Range Queries (e.g., WHERE time > NOW() - INTERVAL '1 hour')
CREATE INDEX IF NOT EXISTS idx_market_time ON market_history (time DESC);


-- TABLE: ohlcv (Candlesticks)
-- Standard OHLCV data for charts
CREATE TABLE IF NOT EXISTS ohlcv (
    time        TIMESTAMPTZ NOT NULL,
    symbol      TEXT NOT NULL,
    timeframe   TEXT NOT NULL,
    open        DOUBLE PRECISION NOT NULL,
    high        DOUBLE PRECISION NOT NULL,
    low         DOUBLE PRECISION NOT NULL,
    close       DOUBLE PRECISION NOT NULL,
    volume      DOUBLE PRECISION NOT NULL,

    PRIMARY KEY (time, symbol, timeframe)
);

SELECT create_hypertable('ohlcv', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol_tf ON ohlcv (symbol, timeframe, time DESC);
