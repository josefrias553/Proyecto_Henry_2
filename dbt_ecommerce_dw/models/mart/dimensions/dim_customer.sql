{{ config(materialized='table') }}

with src as (
    select * from {{ ref('int_customer') }}
),

segment as (
    select customer_id, segment_sk
    from {{ ref('dim_customer_segment') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['src.customer_id']) }} as customer_sk,
    src.customer_id,
    src.nombre as first_name,
    src.apellido as last_name,
    src.email,
    src.fecha_registro as created_at,
    s.segment_sk,
    true as current_flag,
    current_timestamp as valid_from,
    null as valid_to
from src
left join segment s on src.customer_id = s.customer_id