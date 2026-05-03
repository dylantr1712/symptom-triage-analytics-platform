with ranked as (
    select
        *,
        row_number() over (
            partition by session_id
            order by created_at desc
        ) as row_num
    from {{ ref('stg_triage_sessions') }}
)

select
    session_id,
    created_at,
    raw_text,
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
    app_version
from ranked
where row_num = 1
