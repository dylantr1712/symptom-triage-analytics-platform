# Snowflake Setup Checklist

Use this when we reach Snowflake provisioning.

## 1. Create core resources
- Create a warehouse for the app and dbt, for example `TRIAGE_WH`
- Create a database, for example `TRIAGE_PLATFORM`
- Create a schema, for example `RAW`
- Create an analytics schema, for example `ANALYTICS`
- Create a role for the project, for example `TRIAGE_APP_ROLE`
- Create a service user for the app and dbt

## 2. Grant permissions
- Grant warehouse usage to the project role
- Grant database and schema usage to the project role
- Grant create table and insert privileges on the raw schema
- Grant create view and create table privileges on the analytics schema

## 3. Add environment variables
Populate `.env` from `.env.example` with:

- `SNOWFLAKE_ACCOUNT`
- `SNOWFLAKE_USER`
- `SNOWFLAKE_PASSWORD`
- `SNOWFLAKE_WAREHOUSE`
- `SNOWFLAKE_DATABASE`
- `SNOWFLAKE_SCHEMA` set to `ANALYTICS` for dbt target models
- `SNOWFLAKE_RAW_SCHEMA` set to `RAW` for dbt sources
- `SNOWFLAKE_ROLE`

## 4. Copy dbt profile
- Copy `dbt/profiles/profiles.yml.example` to `dbt/profiles/profiles.yml`
- Confirm the environment variables are present
- Run `docker compose run --rm dbt dbt debug --profiles-dir /dbt/profiles`

## 5. Create raw tables
Create these raw tables first:

- `triage_sessions`
- `triage_rule_hits`
- `triage_session_symptoms`

Recommended columns:

### `triage_sessions`
- `session_id`
- `created_at`
- `raw_text`
- `age_years`
- `duration_bucket`
- `severity`
- `triage_level`
- `validation_status`
- `follow_up_question`
- `explanation`
- `next_step`

### `triage_rule_hits`
- `session_id`
- `rule_id`
- `rule_name`
- `matched_on`
- `created_at`

### `triage_session_symptoms`
- `session_id`
- `symptom_code`
- `created_at`

## 6. Validate the pipeline
- Run the Streamlit app locally
- Generate a few sample sessions
- Confirm rows land in Snowflake raw tables
- Run `dbt run --profiles-dir /dbt/profiles`
- Inspect the marts in the analytics schema
