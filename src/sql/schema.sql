CREATE TABLE pipelines (
    id BIGSERIAL PRIMARY KEY,

    name VARCHAR(100) NOT NULL UNIQUE,

    description TEXT,

    owner VARCHAR(100) NOT NULL,

    schedule VARCHAR(100),

    source VARCHAR(255),

    destination VARCHAR(255),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE pipeline_runs (
    id BIGSERIAL PRIMARY KEY,

    pipeline_id BIGINT NOT NULL
        REFERENCES pipelines(id)
        ON DELETE CASCADE,

    run_id UUID NOT NULL UNIQUE,

    started_at TIMESTAMPTZ NOT NULL,

    completed_at TIMESTAMPTZ,

    status VARCHAR(20) NOT NULL,

    rows_read BIGINT NOT NULL DEFAULT 0,

    rows_written BIGINT NOT NULL DEFAULT 0,

    error_message TEXT,

    CONSTRAINT valid_pipeline_status
        CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED'))
);

CREATE TABLE pipeline_logs (
    id BIGSERIAL PRIMARY KEY,

    pipeline_run_id BIGINT NOT NULL
        REFERENCES pipeline_runs(id)
        ON DELETE CASCADE,

    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    level VARCHAR(20) NOT NULL,

    component VARCHAR(100),

    message TEXT NOT NULL
);

CREATE TABLE data_quality_results (
    id BIGSERIAL PRIMARY KEY,

    pipeline_run_id BIGINT NOT NULL
        REFERENCES pipeline_runs(id)
        ON DELETE CASCADE,

    table_name VARCHAR(150) NOT NULL,

    column_name VARCHAR(150),

    check_type VARCHAR(50) NOT NULL,

    total_rows BIGINT NOT NULL,

    failed_rows BIGINT NOT NULL,

    failure_percentage NUMERIC(6,3) NOT NULL,

    status VARCHAR(20) NOT NULL,

    CONSTRAINT valid_quality_status
        CHECK (status IN ('PASS', 'FAIL', 'WARNING'))
);

CREATE TABLE schema_changes (
    id BIGSERIAL PRIMARY KEY,

    table_name VARCHAR(150) NOT NULL,

    column_name VARCHAR(150) NOT NULL,

    change_type VARCHAR(50) NOT NULL,

    old_type VARCHAR(100),

    new_type VARCHAR(100),

    changed_at TIMESTAMPTZ NOT NULL,

    changed_by VARCHAR(100)
);

