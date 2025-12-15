{{ config(materialized='table') }}

with src as (
    select * from {{ ref('int_customer_segment') }}
),
final as (
    select
        {{ dbt_utils.generate_surrogate_key(['customer_id', 'segment_code']) }} as segment_sk,
        customer_id,
        segment_code,
        case segment_code
            when 'LOYAL' then 'Cliente leal'
            when 'ACTIVE' then 'Cliente activo'
            else 'Cliente nuevo'
        end as segment_name,
        case segment_code
            when 'LOYAL' then 'Gold'
            when 'ACTIVE' then 'Silver'
            else 'Bronze'
        end as loyalty_tier,
        case segment_code
            when 'LOYAL' then 0.05
            when 'ACTIVE' then 0.15
            else 0.30
        end as risk_score,
        case segment_code
            when 'LOYAL' then true
            else false
        end as last_behavior_flag,
        'Segmento derivado por antigüedad' as description
    from src
)
select * from final