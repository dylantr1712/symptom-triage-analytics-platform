select
    cast(created_at as date) as event_date,
    count(*) as total_sessions,
    sum(case when insufficient_information_flag then 1 else 0 end) as insufficient_information_sessions,
    round(
        sum(case when insufficient_information_flag then 1 else 0 end) / nullif(count(*), 0),
        4
    ) as insufficient_information_rate
from {{ ref('fct_triage_sessions') }}
group by 1

