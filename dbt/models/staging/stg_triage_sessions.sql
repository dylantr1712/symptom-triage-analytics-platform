select
    session_id,
    created_at,
    raw_text,
    age_years,
    duration_bucket,
    severity,
    triage_level,
    validation_status,
    follow_up_question,
    explanation,
    next_step
from {{ source('raw', 'triage_sessions') }}

