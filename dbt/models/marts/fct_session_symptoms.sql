{{ config(
    materialized='incremental',
    unique_key=['session_id', 'symptom_code'],
    incremental_strategy='merge'
) }}

select
    session_id,
    symptom_code,
    created_at
from {{ ref('stg_triage_session_symptoms') }}

{% if is_incremental() %}
where created_at >= (
    select coalesce(max(created_at), '1900-01-01'::timestamp_ntz)
    from {{ this }}
)
{% endif %}

