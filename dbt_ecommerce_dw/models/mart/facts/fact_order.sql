{{ config(materialized='table') }}

with src as (
    select * from {{ ref('int_order') }}
),
dim_customer as (
    select customer_id, customer_sk from {{ ref('dim_customer') }} where current_flag = true
),
dim_status as (
    select status_code, order_status_sk from {{ ref('dim_order_status') }}
),
dim_time as (
    select date_value, date_sk from {{ ref('dim_time') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['src.orden_id']) }} as order_sk,
    src.orden_id as order_id,
    dc.customer_sk,
    dt.date_sk,
    ds.order_status_sk,
    src.total as total_amount,
    src.item_count,
    src.total_quantity,
    src.fecha_orden as created_at,
    current_timestamp as updated_at
from src
left join dim_customer dc on src.usuario_id = dc.customer_id
left join dim_status ds on lower(src.estado) = ds.status_code
left join dim_time dt on cast(src.fecha_orden as date) = dt.date_value