alter table TRIAGE_PLATFORM.RAW.triage_sessions
    add column if not exists pipeline_status string;

alter table TRIAGE_PLATFORM.RAW.triage_sessions
    add column if not exists raw_openai_response string;

alter table TRIAGE_PLATFORM.RAW.triage_sessions
    add column if not exists unmapped_symptoms variant;

alter table TRIAGE_PLATFORM.RAW.triage_sessions
    add column if not exists severity_reasons variant;

alter table TRIAGE_PLATFORM.RAW.triage_sessions
    add column if not exists app_version string;

grant select, insert on all tables in schema TRIAGE_PLATFORM.RAW to role TRIAGE_APP_ROLE;
grant select, insert on future tables in schema TRIAGE_PLATFORM.RAW to role TRIAGE_APP_ROLE;
grant usage on schema TRIAGE_PLATFORM.ANALYTICS to role TRIAGE_APP_ROLE;
grant create view on schema TRIAGE_PLATFORM.ANALYTICS to role TRIAGE_APP_ROLE;
grant create table on schema TRIAGE_PLATFORM.ANALYTICS to role TRIAGE_APP_ROLE;
