{{ config(materialized='table') }}

with src as (
    select distinct lower(estado) as status_code
    from {{ ref('stg_ordenes') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['status_code']) }} as order_status_sk,
    src.status_code,
    case src.status_code
        when 'pendiente' then 'Pending'
        when 'procesando' then 'Processing'
        when 'completada' then 'Completed'
        when 'enviado' then 'Shipped'
        when 'entregado' then 'Delivered'
        else 'Other'
    end as description
from src
