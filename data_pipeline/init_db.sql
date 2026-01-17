-- TURBO-PLAN X - Database Initialization Script
-- This script runs automatically when TimescaleDB container starts for the first time

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create OHLCV table for candlestick data
CREATE TABLE IF NOT EXISTS ohlcv (
    time TIMESTAMPTZ NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL, -- '1m', '5m', '15m', '1h', '4h', '1d', '1w'
    open NUMERIC NOT NULL,
    high NUMERIC NOT NULL,
    low NUMERIC NOT NULL,
    close NUMERIC NOT NULL,
    volume NUMERIC NOT NULL,
    quote_volume NUMERIC,
    trades_count INTEGER,
    -- Constraints
    CONSTRAINT ohlcv_positive_prices CHECK (open > 0 AND high > 0 AND low > 0 AND close > 0),
    CONSTRAINT ohlcv_high_low CHECK (high >= low),
    CONSTRAINT ohlcv_positive_volume CHECK (volume >= 0)
);

-- Convert to hypertable (TimescaleDB magic for time-series optimization)
SELECT create_hypertable('ohlcv', 'time', if_not_exists => TRUE);

-- Create indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol_time ON ohlcv (symbol, time DESC);
CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol_timeframe_time ON ohlcv (symbol, timeframe, time DESC);

-- Enable compression (saves ~90% storage)
ALTER TABLE ohlcv SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'symbol,timeframe',
  timescaledb.compress_orderby = 'time DESC'
);

-- Add compression policy: compress data older than 7 days
SELECT add_compression_policy('ohlcv', INTERVAL '7 days', if_not_exists => TRUE);

-- Create table for real-time trades
CREATE TABLE IF NOT EXISTS trades (
    time TIMESTAMPTZ NOT NULL,
    symbol TEXT NOT NULL,
    trade_id TEXT,
    price NUMERIC NOT NULL,
    quantity NUMERIC NOT NULL,
    quote_quantity NUMERIC,
    side TEXT, -- 'buy' or 'sell'
    is_buyer_maker BOOLEAN,
    CONSTRAINT trades_positive_price CHECK (price > 0),
    CONSTRAINT trades_positive_quantity CHECK (quantity > 0)
);

SELECT create_hypertable('trades', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_trades_symbol_time ON trades (symbol, time DESC);

ALTER TABLE trades SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'symbol'
);

SELECT add_compression_policy('trades', INTERVAL '3 days', if_not_exists => TRUE);

-- Create table for order book snapshots
CREATE TABLE IF NOT EXISTS orderbook_snapshots (
    time TIMESTAMPTZ NOT NULL,
    symbol TEXT NOT NULL,
    bids JSONB NOT NULL, -- Array of [price, quantity]
    asks JSONB NOT NULL,
    CONSTRAINT orderbook_valid_json CHECK (jsonb_typeof(bids) = 'array' AND jsonb_typeof(asks) = 'array')
);

SELECT create_hypertable('orderbook_snapshots', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_orderbook_symbol_time ON orderbook_snapshots (symbol, time DESC);

-- Create table for AI predictions/signals
CREATE TABLE IF NOT EXISTS ai_signals (
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    symbol TEXT NOT NULL,
    signal_type TEXT NOT NULL, -- 'BUY', 'SELL', 'HOLD'
    confidence NUMERIC CHECK (confidence >= 0 AND confidence <= 1),
    predicted_price NUMERIC,
    timeframe TEXT,
    model_name TEXT,
    metadata JSONB,
    PRIMARY KEY (time, symbol, model_name)
);

SELECT create_hypertable('ai_signals', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_ai_signals_symbol_time ON ai_signals (symbol, time DESC);

-- Create table for agent activity logs
CREATE TABLE IF NOT EXISTS agent_logs (
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    agent_id TEXT NOT NULL,
    agent_type TEXT NOT NULL, -- 'scout', 'analyst', 'hunter', 'defender'
    action TEXT NOT NULL,
    symbol TEXT,
    details JSONB,
    PRIMARY KEY (time, agent_id)
);

SELECT create_hypertable('agent_logs', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_agent_logs_type_time ON agent_logs (agent_type, time DESC);

-- Create materialized view for latest prices (fast access)
CREATE MATERIALIZED VIEW IF NOT EXISTS latest_prices AS
SELECT DISTINCT ON (symbol)
    symbol,
    time,
    close as price,
    volume
FROM ohlcv
WHERE timeframe = '1m'
ORDER BY symbol, time DESC;

CREATE UNIQUE INDEX IF NOT EXISTS idx_latest_prices_symbol ON latest_prices (symbol);

-- Create continuous aggregate for hourly stats (pre-computed)
CREATE MATERIALIZED VIEW IF NOT EXISTS ohlcv_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    symbol,
    first(open, time) as open,
    max(high) as high,
    min(low) as low,
    last(close, time) as close,
    sum(volume) as volume
FROM ohlcv
WHERE timeframe = '1m'
GROUP BY bucket, symbol;

-- Add refresh policy for continuous aggregate
SELECT add_continuous_aggregate_policy('ohlcv_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE);

-- Grant all privileges (for development)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Print success message
DO $$
BEGIN
    RAISE NOTICE '✓ TURBO-PLAN X Database initialized successfully!';
    RAISE NOTICE '  - TimescaleDB extension enabled';
    RAISE NOTICE '  - Tables created: ohlcv, trades, orderbook_snapshots, ai_signals, agent_logs';
    RAISE NOTICE '  - Hypertables configured with compression';
    RAISE NOTICE '  - Indexes and views created';
END $$;
