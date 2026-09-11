INSERT INTO pipelines (
    name,
    description,
    owner,
    schedule,
    source,
    destination,
    environment
)
VALUES
(

    'customer_sync',
    'Synchronizes customer information from the CRM system.',
    'customer-data-team',
    'hourly',
    'CRM',
    'warehouse.customers',
    'production'

),
(
    'daily_sales',
    'Loads daily sales transactions into the analytics warehouse.',
    'analytics-team',
    'daily at 06:00',
    'ERP',
    'warehouse.sales',
    'production'
),
(
    'inventory_sync',
    'Synchronizes inventory levels from the warehouse management system.',
    'supply-chain-team',
    'every 30 minutes',
    'WMS',
    'warehouse.inventory',
    'production'
),
(
    'payment_events',
    'Processes payment events from the payment provider.',
    'payments-team',
    'every 15 minutes',
    'Payment API',
    'warehouse.payment_events',
    'production'
);

INSERT INTO pipeline_dependencies (
    pipeline_id,
    dependency_name,
    dependency_type,
    connection_identifier
)
SELECT p.id, dependency_name, dependency_type, connection_identifier
FROM pipelines p
JOIN (VALUES
    ('customer_sync', 'crm-service', 'SOURCE', 'crm-api'),
    ('daily_sales', 'erp-service', 'SOURCE', 'erp-api'),
    ('inventory_sync', 'warehouse-service', 'SOURCE', 'wms-api'),
    ('payment_events', 'payment-provider', 'SOURCE', 'payment-api')
) AS dependencies(pipeline_name, dependency_name, dependency_type, connection_identifier)
    ON dependencies.pipeline_name = p.name;

INSERT INTO deployments (
    service_name,
    version,
    deployed_at,
    environment,
    deployed_by,
    commit_sha
)
VALUES
('crm-service', '2026.09.10.1', NOW() - INTERVAL '100 minutes', 'production', 'crm-team', 'crm-20260910'),
('erp-service', '2026.09.10.2', NOW() - INTERVAL '200 minutes', 'production', 'analytics-team', 'erp-20260910'),
('warehouse-service', '2026.09.10.3', NOW() - INTERVAL '70 minutes', 'production', 'supply-chain-team', 'wms-20260910'),
('payment-provider', '2026.09.10.4', NOW() - INTERVAL '10 minutes', 'production', 'payments-team', 'pay-20260910');

INSERT INTO pipeline_runs(

    pipeline_id,
    run_id,
    started_at,
    completed_at,
    status,
    rows_read,
    rows_written

)
SELECT 
    p.id,
    gen_random_uuid(),
    run_time,
    run_time+INTERVAL '4 minutes',
    'SUCCESS',
    98000 + FLOOR(RANDOM()*5000)::BIGINT,
    97000 + FLOOR(RANDOM()*5000)::BIGINT

FROM pipelines p
CROSS JOIN LATERAL generate_series(
    NOW()- INTERVAL '3 days',
    NOW()- INTERVAL '2 hours',
    INTERVAL '1 hour'
) AS run_time
WHERE p.name='customer_sync';

INSERT INTO pipeline_runs (
    pipeline_id,
    run_id,
    started_at,
    completed_at,
    status,
    rows_read,
    rows_written
)
SELECT
    p.id,
    gen_random_uuid(),
    run_time,
    run_time + INTERVAL '8 minutes',
    'SUCCESS',
    900000 + FLOOR(RANDOM() * 100000)::BIGINT,
    890000 + FLOOR(RANDOM() * 100000)::BIGINT
FROM pipelines p
CROSS JOIN LATERAL generate_series(
    NOW() - INTERVAL '7 days',
    NOW() - INTERVAL '1 day',
    INTERVAL '1 day'
) AS run_time
WHERE p.name = 'daily_sales';

INSERT INTO pipeline_runs (
    pipeline_id,
    run_id,
    started_at,
    completed_at,
    status,
    rows_read,
    rows_written
)
SELECT
    p.id,
    gen_random_uuid(),
    run_time,
    run_time + INTERVAL '2 minutes',
    'SUCCESS',
    45000 + FLOOR(RANDOM() * 5000)::BIGINT,
    44000 + FLOOR(RANDOM() * 5000)::BIGINT
FROM pipelines p
CROSS JOIN LATERAL generate_series(
    NOW() - INTERVAL '2 days',
    NOW() - INTERVAL '1 hour',
    INTERVAL '30 minutes'
) AS run_time
WHERE p.name = 'inventory_sync';

INSERT INTO pipeline_runs (
    pipeline_id,
    run_id,
    started_at,
    completed_at,
    status,
    rows_read,
    rows_written
)
SELECT
    p.id,
    gen_random_uuid(),
    run_time,
    run_time + INTERVAL '1 minute',
    'SUCCESS',
    5000 + FLOOR(RANDOM() * 1000)::BIGINT,
    4950 + FLOOR(RANDOM() * 1000)::BIGINT
FROM pipelines p
CROSS JOIN LATERAL generate_series(
    NOW() - INTERVAL '1 day',
    NOW() - INTERVAL '30 minutes',
    INTERVAL '15 minutes'
) AS run_time
WHERE p.name = 'payment_events';

INSERT INTO schema_changes(

    table_name,
    column_name,
    change_type,
    old_type,
    new_type,
    changed_at,
    changed_by

)
VALUES(
    'customers',
    'email',
    'TYPE_CHANGED',
    'VARCHAR',
    'JSONB',
    NOW()-INTERVAL '2 hours',
    'crm-team'
);

UPDATE pipeline_runs r
SET error_message = REPLACE(
        r.error_message,
        'Transformation failed:',
        'Schema mismatch:'
)
FROM pipelines p
WHERE p.id = r.pipeline_id
    AND p.name = 'customer_sync'
    AND r.error_message LIKE 'Transformation failed:%';

INSERT INTO pipeline_runs(
    pipeline_id,
    run_id,
    started_at,
    completed_at,
    status,
    rows_read,
    rows_written,
    error_message
)
SELECT
    id,
    gen_random_uuid(),
    NOW()-INTERVAL '90 minutes',
    NOW()-INTERVAL '86 minutes',
    'FAILED',
    101238,
    0,
    'Schema mismatch: cannot cast JSONB value to VARCHAR'

FROM pipelines
WHERE name='customer_sync'
RETURNING id;

INSERT INTO pipeline_logs (
    pipeline_run_id,
    timestamp,
    level,
    component,
    message
)
SELECT
    r.id,
    NOW() - INTERVAL '89 minutes',
    'INFO',
    'extract',
    'Successfully extracted 101238 customer records'
FROM pipeline_runs r
JOIN pipelines p ON p.id = r.pipeline_id
WHERE p.name = 'customer_sync'
  AND r.status = 'FAILED'
  AND r.started_at > NOW() - INTERVAL '2 hours';

INSERT INTO pipeline_runs (
    pipeline_id,
    run_id,
    started_at,
    completed_at,
    status,
    rows_read,
    rows_written,
    error_message
)
SELECT
    id,
    gen_random_uuid(),
    NOW() - INTERVAL '5 minutes',
    NOW() - INTERVAL '1 minute',
    'FAILED',
    101238,
    0,
    'Schema mismatch: crm-service returned an unexpected email type'
FROM pipelines
WHERE name = 'customer_sync';

INSERT INTO pipeline_logs (
    pipeline_run_id,
    timestamp,
    level,
    component,
    message
)
SELECT
    r.id,
    NOW() - INTERVAL '4 minutes',
    'ERROR',
    'crm-service',
    'crm-service returned a schema mismatch for the email column'
FROM pipeline_runs r
JOIN pipelines p ON p.id = r.pipeline_id
WHERE p.name = 'customer_sync'
  AND r.started_at > NOW() - INTERVAL '10 minutes';

INSERT INTO pipeline_logs (
    pipeline_run_id,
    timestamp,
    level,
    component,
    message
)
SELECT
    r.id,
    NOW() - INTERVAL '3 minutes',
    'ERROR',
    'transform',
    'Transformation failed because crm-service sent JSONB instead of VARCHAR'
FROM pipeline_runs r
JOIN pipelines p ON p.id = r.pipeline_id
WHERE p.name = 'customer_sync'
  AND r.started_at > NOW() - INTERVAL '10 minutes';

INSERT INTO pipeline_logs (
    pipeline_run_id,
    timestamp,
    level,
    component,
    message
)
SELECT
    r.id,
    NOW() - INTERVAL '2 minutes',
    'ERROR',
    'pipeline',
    'Pipeline failed after the schema validation step'
FROM pipeline_runs r
JOIN pipelines p ON p.id = r.pipeline_id
WHERE p.name = 'customer_sync'
  AND r.started_at > NOW() - INTERVAL '10 minutes';

INSERT INTO data_quality_results (
    pipeline_run_id,
    table_name,
    column_name,
    check_type,
    total_rows,
    failed_rows,
    failure_percentage,
    status
)
SELECT
    r.id,
    'customers',
    'email',
    'TYPE_CHECK',
    101238,
    101238,
    100.000,
    'FAIL'
FROM pipeline_runs r
JOIN pipelines p ON p.id = r.pipeline_id
WHERE p.name = 'customer_sync'
  AND r.started_at > NOW() - INTERVAL '10 minutes';

INSERT INTO pipeline_logs (
    pipeline_run_id,
    timestamp,
    level,
    component,
    message
)
SELECT
    r.id,
    NOW() - INTERVAL '88 minutes',
    'ERROR',
    'transform',
    'Column email contains JSONB values but transformation expects VARCHAR'
FROM pipeline_runs r
JOIN pipelines p ON p.id = r.pipeline_id
WHERE p.name = 'customer_sync'
  AND r.status = 'FAILED'
  AND r.started_at > NOW() - INTERVAL '2 hours';

INSERT INTO pipeline_logs (
    pipeline_run_id,
    timestamp,
    level,
    component,
    message
)
SELECT
    r.id,
    NOW() - INTERVAL '87 minutes',
    'ERROR',
    'pipeline',
    'Pipeline terminated after transformation failure'
FROM pipeline_runs r
JOIN pipelines p ON p.id = r.pipeline_id
WHERE p.name = 'customer_sync'
  AND r.status = 'FAILED'
  AND r.started_at > NOW() - INTERVAL '2 hours';

INSERT INTO pipeline_runs (
    pipeline_id,
    run_id,
    started_at,
    completed_at,
    status,
    rows_read,
    rows_written,
    error_message
)
SELECT
    id,
    gen_random_uuid(),
    NOW() - INTERVAL '3 hours',
    NOW() - INTERVAL '2 hours 55 minutes',
    'FAILED',
    1250342,
    0,
    'Data quality threshold exceeded for customer_id'
FROM pipelines
WHERE name = 'daily_sales';



INSERT INTO data_quality_results (
    pipeline_run_id,
    table_name,
    column_name,
    check_type,
    total_rows,
    failed_rows,
    failure_percentage,
    status
)
SELECT
    r.id,
    'sales',
    'customer_id',
    'NULL_CHECK',
    1250342,
    300121,
    24.003,
    'FAIL'
FROM pipeline_runs r
JOIN pipelines p ON p.id = r.pipeline_id
WHERE p.name = 'daily_sales'
  AND r.status = 'FAILED'
  AND r.started_at > NOW() - INTERVAL '4 hours';

INSERT INTO data_quality_results (
        pipeline_run_id,
        table_name,
        column_name,
        check_type,
        total_rows,
        failed_rows,
        failure_percentage,
        status
)
SELECT
        r.id,
        'customers',
        'email',
        'TYPE_CHECK',
        101238,
        101238,
        100.000,
        'FAIL'
FROM pipeline_runs r
JOIN pipelines p ON p.id = r.pipeline_id
WHERE p.name = 'customer_sync'
    AND r.status = 'FAILED'
    AND r.started_at > NOW() - INTERVAL '2 hours';

INSERT INTO pipeline_logs (
    pipeline_run_id,
    timestamp,
    level,
    component,
    message
)
SELECT
    r.id,
    NOW() - INTERVAL '2 hours 58 minutes',
    'ERROR',
    'data-quality',
    'NULL rate for customer_id exceeded threshold of 1%'
FROM pipeline_runs r
JOIN pipelines p ON p.id = r.pipeline_id
WHERE p.name = 'daily_sales'
  AND r.status = 'FAILED'
  AND r.started_at > NOW() - INTERVAL '4 hours';

INSERT INTO pipeline_runs (
    pipeline_id,
    run_id,
    started_at,
    completed_at,
    status,
    rows_read,
    rows_written,
    error_message
)
SELECT
    id,
    gen_random_uuid(),
    NOW() - INTERVAL '45 minutes',
    NOW() - INTERVAL '42 minutes',
    'FAILED',
    4213,
    4102,
    'Source record volume below minimum threshold'
FROM pipelines
WHERE name = 'inventory_sync';

INSERT INTO pipeline_logs (
    pipeline_run_id,
    timestamp,
    level,
    component,
    message
)
SELECT
    r.id,
    NOW() - INTERVAL '43 minutes',
    'ERROR',
    'validation',
    'Expected at least 40000 records but received 4213'
FROM pipeline_runs r
JOIN pipelines p ON p.id = r.pipeline_id
WHERE p.name = 'inventory_sync'
  AND r.status = 'FAILED'
  AND r.started_at > NOW() - INTERVAL '1 hour';

INSERT INTO data_quality_results (
        pipeline_run_id,
        table_name,
        column_name,
        check_type,
        total_rows,
        failed_rows,
        failure_percentage,
        status
)
SELECT
        r.id,
        'inventory',
        NULL,
        'ROW_COUNT_CHECK',
        4213,
        4213,
        100.000,
        'WARNING'
FROM pipeline_runs r
JOIN pipelines p ON p.id = r.pipeline_id
WHERE p.name = 'inventory_sync'
    AND r.status = 'FAILED'
    AND r.started_at > NOW() - INTERVAL '1 hour';


INSERT INTO pipeline_runs (
    pipeline_id,
    run_id,
    started_at,
    completed_at,
    status,
    rows_read,
    rows_written,
    error_message
)
SELECT
    id,
    gen_random_uuid(),
    NOW() - INTERVAL '20 minutes',
    NOW() - INTERVAL '15 minutes',
    'FAILED',
    0,
    0,
    'PostgreSQL connection timeout after 3 retries'
FROM pipelines
WHERE name = 'payment_events';

INSERT INTO data_quality_results (
        pipeline_run_id,
        table_name,
        column_name,
        check_type,
        total_rows,
        failed_rows,
        failure_percentage,
        status
)
SELECT
        r.id,
        'payment_events',
        NULL,
        'ROW_COUNT_CHECK',
        0,
        0,
        0.000,
        'PASS'
FROM pipeline_runs r
JOIN pipelines p ON p.id = r.pipeline_id
WHERE p.name = 'payment_events'
    AND r.status = 'FAILED'
    AND r.started_at > NOW() - INTERVAL '30 minutes';

INSERT INTO pipeline_logs (
    pipeline_run_id,
    timestamp,
    level,
    component,
    message
)
SELECT
    r.id,
    NOW() - INTERVAL '19 minutes',
    'ERROR',
    'database',
    'Connection timeout while connecting to warehouse PostgreSQL'
FROM pipeline_runs r
JOIN pipelines p ON p.id = r.pipeline_id
WHERE p.name = 'payment_events'
  AND r.status = 'FAILED'
  AND r.started_at > NOW() - INTERVAL '30 minutes';

INSERT INTO pipeline_logs (
    pipeline_run_id,
    timestamp,
    level,
    component,
    message
)
SELECT
    r.id,
    NOW() - INTERVAL '16 minutes',
    'ERROR',
    'database',
    'All 3 connection retry attempts failed'
FROM pipeline_runs r
JOIN pipelines p ON p.id = r.pipeline_id
WHERE p.name = 'payment_events'
  AND r.status = 'FAILED'
  AND r.started_at > NOW() - INTERVAL '30 minutes';

