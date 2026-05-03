select
    cast(created_at as date) as event_date,
    flattened.value::string as unmapped_symptom,
    count(*) as occurrence_count
from {{ ref('fct_triage_sessions') }},
    lateral flatten(input => unmapped_symptoms) as flattened
where flattened.value is not null
group by 1, 2

