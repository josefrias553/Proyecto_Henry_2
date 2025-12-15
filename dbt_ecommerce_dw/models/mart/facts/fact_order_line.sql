{{ config(materialized='table') }}

with src as (
    select * from {{ ref('int_order_line') }}
),
dim_customer as (
    select customer_id, customer_sk from {{ ref('dim_customer') }} where current_flag = true
),
dim_product as (
    select product_id, product_sk from {{ ref('dim_product') }} where current_flag = true
),
dim_time as (
    select date_value, date_sk from {{ ref('dim_time') }}
),
fact_order as (
    select order_id, order_sk from {{ ref('fact_order') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['src.detalle_id']) }} as order_line_sk,
    src.orden_id as order_id,
    fo.order_sk,
    dc.customer_sk,
    dp.product_sk,
    dt.date_sk,
    src.cantidad as quantity,
    src.precio_unitario as price_unit,
    src.total,
    src.fecha_orden as created_at,
    current_timestamp as updated_at
from src
left join dim_customer dc on src.usuario_id = dc.customer_id
left join dim_product dp on src.producto_id = dp.product_id
left join dim_time dt on cast(src.fecha_orden as date) = dt.date_value
left join fact_order fo on src.orden_id = fo.order_id