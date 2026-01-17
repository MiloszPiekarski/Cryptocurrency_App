-- CASH MAELSTROM Database Schema
-- Optimization: High-traffic columns indexed. 
-- Partitioning strategy recommended for market_history if size > 100GB.

-- 1. Market History Table
CREATE TABLE market_history (
    id SERIAL PRIMARY KEY,
    asset_pair VARCHAR(20) NOT NULL, -- e.g., 'BTC/USDT'
    price DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(24, 8) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50), -- 'Binance', 'Bybit'
    sentiment_score FLOAT
);

-- Indexing Strategy for Market History
-- High cardinality high traffic columns
CREATE INDEX idx_market_history_asset_pair ON market_history(asset_pair);
CREATE INDEX idx_market_history_timestamp ON market_history(timestamp DESC);
-- Composite index for common query: Get price history for asset X ordered by time
CREATE INDEX idx_market_history_asset_time ON market_history(asset_pair, timestamp DESC);

-- 2. Agent Logs Table
CREATE TABLE agent_logs (
    id BIGSERIAL PRIMARY KEY,
    agent_id UUID NOT NULL,
    agent_role VARCHAR(50) NOT NULL,
    log_level VARCHAR(10) DEFAULT 'INFO',
    message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexing Strategy for Agent Logs
CREATE INDEX idx_agent_logs_agent_id ON agent_logs(agent_id);
-- Full Text Search Index for searching specific error messages or patterns in logs
CREATE INDEX idx_agent_logs_message_gin ON agent_logs USING gin(to_tsvector('english', message));

-- 3. Whale Movements Table
CREATE TABLE whale_movements (
    id SERIAL PRIMARY KEY,
    transaction_hash VARCHAR(66) UNIQUE NOT NULL,
    wallet_address VARCHAR(42) NOT NULL,
    asset_symbol VARCHAR(10) NOT NULL,
    amount DECIMAL(30, 8) NOT NULL,
    amount_usd DECIMAL(20, 2),
    transaction_type VARCHAR(20), -- 'INFLOW', 'OUTFLOW'
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Indexing Strategy for Whale Movements
-- Unique index is already enforced by UNIQUE constraint on transaction_hash, mostly B-tree by default
CREATE INDEX idx_whale_movements_wallet ON whale_movements(wallet_address);
CREATE INDEX idx_whale_movements_amount_usd ON whale_movements(amount_usd DESC); 
-- Index to quickly find large movements recently
CREATE INDEX idx_whale_high_value_recent ON whale_movements(timestamp DESC) WHERE amount_usd > 1000000;

-- Optimization Analysis:
-- 1. Timestamps are heavily indexed as most queries will be time-series based.
-- 2. Asset pairs and Wallet addresses are indexed for filtering.
-- 3. GIN index used for text search in logs to avoid slow LIKE '%...%' queries.
-- 4. Partial index on whale_movements focuses only on significant transactions to save index size.
