-- Create Database (if not exists)
SELECT 'CREATE DATABASE turboplanx' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'turboplanx')\gexec

\c turboplanx

-- Enable TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create Hypertable
CREATE TABLE IF NOT EXISTS ohlcv (
    time TIMESTAMPTZ NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    open NUMERIC NOT NULL,
    high NUMERIC NOT NULL,
    low NUMERIC NOT NULL,
    close NUMERIC NOT NULL,
    volume NUMERIC NOT NULL
);

-- Convert to Hypertable (only if not already)

CREATE TABLE IF NOT EXISTS users (
    uid TEXT PRIMARY KEY,
    email TEXT,
    plan TEXT DEFAULT 'FREE',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_watchlist (
    user_id TEXT NOT NULL REFERENCES users(uid),
    symbol TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, symbol)
);

-- Indexes
CREATE INDEX IF NOT EXISTS ohlcv_symbol_time_idx ON ohlcv (symbol, time DESC);
CREATE INDEX IF NOT EXISTS ohlcv_symbol_tf_time_idx ON ohlcv (symbol, timeframe, time DESC);

-- Compression
ALTER TABLE ohlcv SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'symbol,timeframe'
);

SELECT add_compression_policy('ohlcv', INTERVAL '7 days', if_not_exists => TRUE);
