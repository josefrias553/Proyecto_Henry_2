{{ config(materialized='table') }}

with src as (
    select * from {{ ref('stg_metodospago') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['metodo_pago_id']) }} as payment_method_sk,
    cast(src.metodo_pago_id as int) as payment_method_id,
    src.nombre as name,
    src.descripcion as description
from src