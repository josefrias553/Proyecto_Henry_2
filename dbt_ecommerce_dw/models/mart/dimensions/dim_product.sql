{{ config(materialized='table') }}

with src as (
    select * from {{ ref('int_product') }}
),

final as (
    select
        {{ dbt_utils.generate_surrogate_key(['producto_id']) }} as product_sk,
        producto_id as product_id,
        nombre as name,
        descripcion as description,
        categoria_id as category_id,
        categoria_nombre as category_name,
        precio as current_price,
        true as current_flag,
        current_timestamp as valid_from,
        null as valid_to
    from src
)

select * from final