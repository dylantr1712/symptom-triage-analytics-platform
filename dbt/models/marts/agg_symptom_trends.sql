select
    cast(s.created_at as date) as event_date,
    s.symptom_code,
    count(*) as symptom_count
from {{ ref('fct_session_symptoms') }} as s
group by 1, 2

