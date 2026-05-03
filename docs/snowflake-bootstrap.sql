create warehouse if not exists TRIAGE_WH
    warehouse_size = 'XSMALL'
    auto_suspend = 60
    auto_resume = true;

create database if not exists TRIAGE_PLATFORM;

create schema if not exists TRIAGE_PLATFORM.RAW;
create schema if not exists TRIAGE_PLATFORM.ANALYTICS;

create role if not exists TRIAGE_APP_ROLE;

grant usage on warehouse TRIAGE_WH to role TRIAGE_APP_ROLE;
grant usage on database TRIAGE_PLATFORM to role TRIAGE_APP_ROLE;
grant usage on schema TRIAGE_PLATFORM.RAW to role TRIAGE_APP_ROLE;
grant usage on schema TRIAGE_PLATFORM.ANALYTICS to role TRIAGE_APP_ROLE;
grant create table on schema TRIAGE_PLATFORM.RAW to role TRIAGE_APP_ROLE;
grant create view on schema TRIAGE_PLATFORM.ANALYTICS to role TRIAGE_APP_ROLE;
grant create table on schema TRIAGE_PLATFORM.ANALYTICS to role TRIAGE_APP_ROLE;

create or replace table TRIAGE_PLATFORM.RAW.triage_sessions (
    session_id string,
    created_at timestamp_ntz,
    raw_text string,
    age_years integer,
    duration_bucket string,
    severity string,
    triage_level string,
    validation_status string,
    follow_up_question string,
    explanation string,
    next_step string
);

create or replace table TRIAGE_PLATFORM.RAW.triage_rule_hits (
    session_id string,
    rule_id string,
    rule_name string,
    matched_on variant,
    created_at timestamp_ntz
);

create or replace table TRIAGE_PLATFORM.RAW.triage_session_symptoms (
    session_id string,
    symptom_code string,
    created_at timestamp_ntz
);
