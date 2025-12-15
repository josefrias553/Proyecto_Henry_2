select
    usuario_id as customer_id,
    case
        when fecha_registro < current_date - interval '2 years' then 'LOYAL'
        when fecha_registro < current_date - interval '6 months' then 'ACTIVE'
        else 'NEW'
    end as segment_code
from {{ ref('stg_usuarios') }}