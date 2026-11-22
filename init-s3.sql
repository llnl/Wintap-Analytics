-- Wintap one-off DuckDB session bootstrap.
--
-- Start with:
--   duckdb -init init.sql one-off.duckdb
--
-- This file intentionally reads the same environment variables used by
-- Wintappy/HostActivity. It does not read or print AWS key material.

INSTALL httpfs;
LOAD httpfs;
SET TimeZone='UTC';

-- Keep the secret definition aligned with the Wintappy DBT source contract.
-- DuckDB's CREATE SECRET option parser does not accept compound expressions
-- such as COALESCE directly as option values. Resolve the environment first,
-- render a literal statement, and then let the CLI execute that statement.
-- Only non-secret configuration is written to this temporary file.
COPY (
    WITH config AS (
        SELECT
            nullif(getenv('AWS_PROFILE'), '') AS profile,
            coalesce(
                nullif(getenv('AWS_DEFAULT_REGION'), ''),
                nullif(getenv('AWS_REGION'), '')
            ) AS region,
            nullif(
                regexp_replace(
                    regexp_replace(getenv('AWS_ENDPOINT_URL'), '^https?://', ''),
                    '/$',
                    ''
                ),
                ''
            ) AS endpoint,
            lower(coalesce(nullif(getenv('DUCKDB_USE_SSL'), ''), 'true')) AS use_ssl
    )
    SELECT
        'CREATE OR REPLACE SECRET wintap_raw_sensor '
        || '(TYPE S3, PROVIDER CREDENTIAL_CHAIN'
        || CASE
            WHEN profile IS NOT NULL
            THEN ', CHAIN ''config'', PROFILE '''
                || replace(profile, '''', '''''') || ''''
            ELSE ''
        END
        || CASE
            WHEN region IS NOT NULL
            THEN ', REGION ''' || replace(region, '''', '''''') || ''''
            ELSE ''
        END
        || CASE
            WHEN endpoint IS NOT NULL
            THEN ', ENDPOINT ''' || replace(endpoint, '''', '''''')
                || ''', URL_STYLE ''path'''
            ELSE ''
        END
        || ', USE_SSL '
        || CASE
            WHEN use_ssl IN ('1', 'true', 'yes', 'on') THEN 'true'
            WHEN use_ssl IN ('0', 'false', 'no', 'off') THEN 'false'
            ELSE CAST(error('DUCKDB_USE_SSL must be true or false') AS VARCHAR)
        END
        || ');'
    FROM config
) TO '/tmp/wintap-duckdb-init-secret.sql'
    (FORMAT CSV, HEADER false, QUOTE '');

.read /tmp/wintap-duckdb-init-secret.sql