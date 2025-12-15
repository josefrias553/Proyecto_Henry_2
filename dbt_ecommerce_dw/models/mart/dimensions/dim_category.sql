{{ config(materialized='table') }}

with src as (
    select * from {{ ref('int_category') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['src.categoria_id']) }} as category_sk,
    src.categoria_id as category_id,
    src.nombre as name,
    src.descripcion as description
from src