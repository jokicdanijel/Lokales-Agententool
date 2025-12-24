-- ELION Hyper-Dashboard – PostgreSQL Schema
-- Production Database Initialization

-- Users table
CREATE TABLE
IF NOT EXISTS users
(
    user_id VARCHAR
(64) PRIMARY KEY,
    name VARCHAR
(100) NOT NULL,
    email VARCHAR
(255) UNIQUE NOT NULL,
    password_hash VARCHAR
(255) NOT NULL,
    plan_id VARCHAR
(50) NOT NULL,

    -- Trial
    trial_enabled BOOLEAN DEFAULT TRUE,
    trial_started_at TIMESTAMP,
    trial_day INTEGER DEFAULT 0,

    -- Subscription
    subscription_status VARCHAR
(50) DEFAULT 'trial',
    subscription_started_at TIMESTAMP,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW
(),
    updated_at TIMESTAMP DEFAULT NOW
(),
    last_login TIMESTAMP
);

-- Sessions table
CREATE TABLE
IF NOT EXISTS sessions
(
    session_id VARCHAR
(255) PRIMARY KEY,
    user_id VARCHAR
(64) REFERENCES users
(user_id) ON
DELETE CASCADE,
    created_at TIMESTAMP
DEFAULT NOW
(),
    expires_at TIMESTAMP NOT NULL
);

-- Subscriptions table
CREATE TABLE
IF NOT EXISTS subscriptions
(
    subscription_id SERIAL PRIMARY KEY,
    user_id VARCHAR
(64) REFERENCES users
(user_id) ON
DELETE CASCADE,
    plan_id VARCHAR(50)
NOT NULL,
    status VARCHAR
(50) DEFAULT 'trial',

    -- Billing
    billing_period VARCHAR
(20) DEFAULT 'monthly',
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    next_billing_date TIMESTAMP,

    -- Plan changes
    pending_plan_change VARCHAR
(50),
    pending_change_at TIMESTAMP,

    -- Payment
    payment_method VARCHAR
(100),
    last_payment_date TIMESTAMP,
    last_payment_amount DECIMAL
(10, 2),

    created_at TIMESTAMP DEFAULT NOW
(),
    updated_at TIMESTAMP DEFAULT NOW
()
);

-- Workflows table
CREATE TABLE
IF NOT EXISTS workflows
(
    workflow_id VARCHAR
(64) PRIMARY KEY,
    user_id VARCHAR
(64) REFERENCES users
(user_id) ON
DELETE CASCADE,
    name VARCHAR(100)
NOT NULL,
    description TEXT,
    scope VARCHAR
(50) NOT NULL,
    agent_id VARCHAR
(20),

    enabled BOOLEAN DEFAULT TRUE,
    trigger JSONB,
    steps JSONB NOT NULL,
    limits JSONB,

    created_at TIMESTAMP DEFAULT NOW
(),
    updated_at TIMESTAMP DEFAULT NOW
(),
    last_run_at TIMESTAMP,
    run_count INTEGER DEFAULT 0
);

-- Workflow runs table
CREATE TABLE
IF NOT EXISTS workflow_runs
(
    run_id VARCHAR
(64) PRIMARY KEY,
    workflow_id VARCHAR
(64) REFERENCES workflows
(workflow_id) ON
DELETE CASCADE,
    status VARCHAR(50)
DEFAULT 'pending',

    started_at TIMESTAMP DEFAULT NOW
(),
    completed_at TIMESTAMP,

    steps_completed INTEGER DEFAULT 0,
    steps_total INTEGER NOT NULL,

    results JSONB,
    error TEXT,
    trace_id VARCHAR
(64) NOT NULL
);

-- Archive table (opena2)
CREATE TABLE
IF NOT EXISTS archive
(
    archive_id SERIAL PRIMARY KEY,
    type VARCHAR
(50) NOT NULL,
    agent_id VARCHAR
(20),
    user_id VARCHAR
(64),

    data JSONB NOT NULL,

    created_at TIMESTAMP DEFAULT NOW
()
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_workflows_user_id ON workflows(user_id);
CREATE INDEX idx_workflows_agent_id ON workflows(agent_id);
CREATE INDEX idx_workflow_runs_workflow_id ON workflow_runs(workflow_id);
CREATE INDEX idx_workflow_runs_status ON workflow_runs(status);
CREATE INDEX idx_archive_type ON archive(type);
CREATE INDEX idx_archive_agent_id ON archive(agent_id);
CREATE INDEX idx_archive_created_at ON archive(created_at);

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column
()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW
();
RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE
UPDATE ON users
    FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column
();

CREATE TRIGGER update_subscriptions_updated_at BEFORE
UPDATE ON subscriptions
    FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column
();

CREATE TRIGGER update_workflows_updated_at BEFORE
UPDATE ON workflows
    FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column
();
