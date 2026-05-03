select
    session_id,
    symptom_code,
    created_at
from {{ source('raw', 'triage_session_symptoms') }}

