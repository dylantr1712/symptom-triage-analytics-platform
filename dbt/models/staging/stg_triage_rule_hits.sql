select
    session_id,
    rule_id,
    rule_name,
    matched_on,
    created_at
from {{ source('raw', 'triage_rule_hits') }}

