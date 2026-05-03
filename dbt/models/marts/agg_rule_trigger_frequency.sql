select
    cast(created_at as date) as event_date,
    rule_id,
    rule_name,
    count(*) as trigger_count
from {{ ref('fct_triage_rule_hits') }}
group by 1, 2, 3

