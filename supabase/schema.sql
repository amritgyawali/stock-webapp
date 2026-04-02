-- ============================================================
-- NEPSE Stock Analysis Web App — Supabase SQL Schema
-- ============================================================
-- Run this entire script in your Supabase SQL Editor (Dashboard > SQL Editor > New Query)
-- This creates all tables, indexes, RLS policies, and helper functions.
-- ============================================================

-- =========================
-- 1. STOCKS TABLE
-- Master list of all NEPSE-listed companies
-- =========================
CREATE TABLE IF NOT EXISTS stocks (
    id              BIGSERIAL PRIMARY KEY,
    symbol          VARCHAR(20) NOT NULL UNIQUE,          -- e.g., 'NABIL', 'NICA'
    name            VARCHAR(255),                          -- Full company name
    sector          VARCHAR(100),                          -- e.g., 'Commercial Banks', 'Hydropower'
    is_active       BOOLEAN DEFAULT TRUE,                  -- Whether the stock is actively traded
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast symbol lookups
CREATE INDEX IF NOT EXISTS idx_stocks_symbol ON stocks(symbol);
CREATE INDEX IF NOT EXISTS idx_stocks_sector ON stocks(sector);
CREATE INDEX IF NOT EXISTS idx_stocks_active ON stocks(is_active) WHERE is_active = TRUE;

-- =========================
-- 2. DAILY PRICES TABLE
-- Historical OHLCV data + computed technical indicators
-- =========================
CREATE TABLE IF NOT EXISTS daily_prices (
    id              BIGSERIAL PRIMARY KEY,
    stock_id        BIGINT NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    date            DATE NOT NULL,                         -- Trading date
    open            NUMERIC(12, 2),                        -- Opening price
    high            NUMERIC(12, 2),                        -- Day high
    low             NUMERIC(12, 2),                        -- Day low
    close           NUMERIC(12, 2) NOT NULL,               -- Closing price (LTP)
    prev_close      NUMERIC(12, 2),                        -- Previous day close
    volume          BIGINT DEFAULT 0,                      -- Shares traded
    turnover        NUMERIC(18, 2) DEFAULT 0,              -- Total turnover in Rs.
    change_pct      NUMERIC(8, 4),                         -- Daily change percentage
    -- Technical Indicators (computed by Python script)
    rsi_14          NUMERIC(8, 4),                         -- 14-day RSI
    sma_50          NUMERIC(12, 2),                        -- 50-day Simple Moving Average
    sma_200         NUMERIC(12, 2),                        -- 200-day Simple Moving Average
    ema_12          NUMERIC(12, 2),                        -- 12-day Exponential Moving Average
    ema_26          NUMERIC(12, 2),                        -- 26-day Exponential Moving Average
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    -- Prevent duplicate entries for the same stock on the same date
    CONSTRAINT uq_daily_prices_stock_date UNIQUE (stock_id, date)
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_daily_prices_date ON daily_prices(date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_prices_stock_id ON daily_prices(stock_id);
CREATE INDEX IF NOT EXISTS idx_daily_prices_stock_date ON daily_prices(stock_id, date DESC);

-- =========================
-- 3. PREDICTIONS TABLE
-- ML model predictions for each stock each day
-- =========================
CREATE TABLE IF NOT EXISTS predictions (
    id                  BIGSERIAL PRIMARY KEY,
    stock_id            BIGINT NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    prediction_date     DATE NOT NULL,                     -- Date the prediction is for
    predicted_close     NUMERIC(12, 2) NOT NULL,           -- ML-predicted closing price
    actual_close        NUMERIC(12, 2),                    -- Filled in after market close
    current_price       NUMERIC(12, 2),                    -- Price at time of prediction
    predicted_change_pct NUMERIC(8, 4),                    -- Predicted % change from current
    confidence_score    NUMERIC(5, 4),                      -- Model confidence (0 to 1)
    buy_rank            SMALLINT,                           -- 1-5 for "Top 5 Best Stocks" (NULL if not ranked)
    buy_score           NUMERIC(8, 4),                      -- Composite buy signal score
    model_version       VARCHAR(50) DEFAULT 'rf_v1',       -- Model identifier for tracking
    features_used       JSONB,                              -- JSON of feature values used for this prediction
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    -- Prevent duplicate predictions for same stock on same date
    CONSTRAINT uq_predictions_stock_date UNIQUE (stock_id, prediction_date)
);

-- Indexes for dashboard queries
CREATE INDEX IF NOT EXISTS idx_predictions_date ON predictions(prediction_date DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_buy_rank ON predictions(prediction_date, buy_rank) WHERE buy_rank IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_predictions_stock_date ON predictions(stock_id, prediction_date DESC);

-- =========================
-- 4. MODEL ACCURACY TABLE
-- Daily aggregate accuracy metrics
-- =========================
CREATE TABLE IF NOT EXISTS model_accuracy (
    id                  BIGSERIAL PRIMARY KEY,
    date                DATE NOT NULL UNIQUE,               -- Date these metrics cover
    avg_error_pct       NUMERIC(8, 4),                      -- Average absolute error %
    median_error_pct    NUMERIC(8, 4),                      -- Median absolute error %
    top5_accuracy_pct   NUMERIC(8, 4),                      -- Accuracy for top 5 picks specifically
    total_predictions   INTEGER DEFAULT 0,                  -- Total predictions made that day
    correct_direction   INTEGER DEFAULT 0,                  -- Predictions with correct up/down direction
    direction_accuracy  NUMERIC(8, 4),                      -- % of correct direction predictions
    model_version       VARCHAR(50) DEFAULT 'rf_v1',
    metadata            JSONB,                              -- Additional stats in JSON
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_model_accuracy_date ON model_accuracy(date DESC);

-- =========================
-- 5. MARKET SUMMARY TABLE
-- Daily NEPSE market-level data
-- =========================
CREATE TABLE IF NOT EXISTS market_summary (
    id                  BIGSERIAL PRIMARY KEY,
    date                DATE NOT NULL UNIQUE,
    nepse_index         NUMERIC(12, 2),                     -- NEPSE Index value
    nepse_change        NUMERIC(8, 2),                      -- Change in points
    nepse_change_pct    NUMERIC(8, 4),                      -- Change in %
    total_turnover      NUMERIC(18, 2),                     -- Total turnover Rs.
    total_traded_shares BIGINT,                              -- Total traded shares
    total_transactions  INTEGER,                             -- Total number of transactions
    total_scrips_traded INTEGER,                              -- Number of stocks traded
    market_status       VARCHAR(20) DEFAULT 'closed',        -- 'open', 'closed', 'pre-open'
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_market_summary_date ON market_summary(date DESC);

-- =========================
-- 6. HELPER FUNCTIONS
-- =========================

-- Auto-update the updated_at timestamp on stocks table
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_stocks_updated_at
    BEFORE UPDATE ON stocks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically fill actual_close in predictions
-- Called by a scheduled function or the Python script after market close
CREATE OR REPLACE FUNCTION fill_actual_close(target_date DATE)
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    UPDATE predictions p
    SET actual_close = dp.close,
        predicted_change_pct = CASE
            WHEN p.current_price > 0
            THEN ((dp.close - p.current_price) / p.current_price) * 100
            ELSE NULL
        END
    FROM daily_prices dp
    WHERE p.stock_id = dp.stock_id
      AND p.prediction_date = dp.date
      AND dp.date = target_date
      AND p.actual_close IS NULL;

    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

-- View: Today's Top Picks (convenience view for the dashboard)
CREATE OR REPLACE VIEW v_todays_top_picks AS
SELECT
    p.prediction_date,
    s.symbol,
    s.name,
    s.sector,
    p.current_price,
    p.predicted_close,
    p.predicted_change_pct,
    p.confidence_score,
    p.buy_rank,
    p.buy_score,
    p.model_version
FROM predictions p
JOIN stocks s ON s.id = p.stock_id
WHERE p.prediction_date = CURRENT_DATE
  AND p.buy_rank IS NOT NULL
ORDER BY p.buy_rank ASC;

-- View: Latest predictions with stock details
CREATE OR REPLACE VIEW v_latest_predictions AS
SELECT
    p.prediction_date,
    s.symbol,
    s.name,
    s.sector,
    p.current_price,
    p.predicted_close,
    p.predicted_change_pct,
    p.confidence_score,
    p.buy_rank,
    p.actual_close,
    CASE
        WHEN p.actual_close IS NOT NULL AND p.current_price > 0
        THEN ABS(p.predicted_close - p.actual_close) / p.current_price * 100
        ELSE NULL
    END AS error_pct,
    p.model_version
FROM predictions p
JOIN stocks s ON s.id = p.stock_id
WHERE p.prediction_date = (
    SELECT MAX(prediction_date) FROM predictions
)
ORDER BY p.buy_rank ASC NULLS LAST, s.symbol ASC;

-- View: Model accuracy over time (for charts)
CREATE OR REPLACE VIEW v_accuracy_history AS
SELECT
    date,
    avg_error_pct,
    median_error_pct,
    top5_accuracy_pct,
    direction_accuracy,
    total_predictions,
    correct_direction,
    model_version
FROM model_accuracy
ORDER BY date DESC
LIMIT 90;

-- =========================
-- 7. ROW LEVEL SECURITY (RLS)
-- =========================

-- Enable RLS on all tables
ALTER TABLE stocks ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_prices ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_accuracy ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_summary ENABLE ROW LEVEL SECURITY;

-- PUBLIC READ policies (for the Next.js dashboard using anon key)
CREATE POLICY "Allow public read on stocks"
    ON stocks FOR SELECT
    USING (true);

CREATE POLICY "Allow public read on daily_prices"
    ON daily_prices FOR SELECT
    USING (true);

CREATE POLICY "Allow public read on predictions"
    ON predictions FOR SELECT
    USING (true);

CREATE POLICY "Allow public read on model_accuracy"
    ON model_accuracy FOR SELECT
    USING (true);

CREATE POLICY "Allow public read on market_summary"
    ON market_summary FOR SELECT
    USING (true);

-- SERVICE ROLE WRITE policies (for the Python script using service_role key)
-- Note: service_role key bypasses RLS by default in Supabase,
-- but we add these for completeness and if you ever change settings.
CREATE POLICY "Allow service role insert on stocks"
    ON stocks FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Allow service role update on stocks"
    ON stocks FOR UPDATE
    USING (true);

CREATE POLICY "Allow service role insert on daily_prices"
    ON daily_prices FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Allow service role update on daily_prices"
    ON daily_prices FOR UPDATE
    USING (true);

CREATE POLICY "Allow service role insert on predictions"
    ON predictions FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Allow service role update on predictions"
    ON predictions FOR UPDATE
    USING (true);

CREATE POLICY "Allow service role insert on model_accuracy"
    ON model_accuracy FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Allow service role update on model_accuracy"
    ON model_accuracy FOR UPDATE
    USING (true);

CREATE POLICY "Allow service role insert on market_summary"
    ON market_summary FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Allow service role update on market_summary"
    ON market_summary FOR UPDATE
    USING (true);

-- =========================
-- DONE! ✅
-- =========================
-- Your database is now ready.
-- Next step: Set up the Python script and add your
-- SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY as environment variables.
