{{ config(materialized='table') }}

with src as (
    select * from {{ ref('int_address') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['direccion_id']) }} as address_sk,
    cast(direccion_id as int) as address_id,
    cast(usuario_id as int) as customer_id,
    calle as street,
    ciudad as city,
    provincia as state,
    pais as country,
    codigo_postal as postal_code,
    true as current_flag,
    current_timestamp as valid_from,
    null as valid_to
from src