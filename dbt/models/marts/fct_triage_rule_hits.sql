{{ config(
    materialized='incremental',
    unique_key=['session_id', 'rule_id'],
    incremental_strategy='merge'
) }}

select
    session_id,
    rule_id,
    rule_name,
    matched_on,
    created_at
from {{ ref('stg_triage_rule_hits') }}

{% if is_incremental() %}
where created_at >= (
    select coalesce(max(created_at), '1900-01-01'::timestamp_ntz)
    from {{ this }}
)
{% endif %}

