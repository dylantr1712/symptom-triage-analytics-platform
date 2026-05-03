select
    cast(created_at as date) as event_date,
    triage_level,
    count(*) as session_count,
    sum(case when insufficient_information_flag then 1 else 0 end) as insufficient_information_count
from {{ ref('fct_triage_sessions') }}
group by 1, 2

