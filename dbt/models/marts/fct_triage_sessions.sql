{{ config(
    materialized='incremental',
    unique_key='session_id',
    incremental_strategy='merge'
) }}

select
    session_id,
    created_at,
    age_years,
    duration_bucket,
    severity,
    triage_level,
    pipeline_status,
    validation_status,
    follow_up_question,
    explanation,
    next_step,
    raw_openai_response,
    unmapped_symptoms,
    severity_reasons,
    app_version,
    case when validation_status = 'INSUFFICIENT_INFORMATION' then true else false end as insufficient_information_flag
from {{ ref('int_session_latest_decision') }}

{% if is_incremental() %}
where created_at >= (
    select coalesce(max(created_at), '1900-01-01'::timestamp_ntz)
    from {{ this }}
)
{% endif %}
