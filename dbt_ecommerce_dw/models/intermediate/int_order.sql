with ordenes as (
    select * from {{ ref('stg_ordenes') }}
),
detalle as (
    select orden_id, count(*) as items, sum(cantidad) as total_quantity
    from {{ ref('stg_detalleordenes') }}
    group by orden_id
)

select
    o.orden_id,
    o.usuario_id,
    o.fecha_orden,
    o.total,
    o.estado,
    coalesce(d.items, 0) as item_count,
    coalesce(d.total_quantity, 0) as total_quantity
from ordenes o
left join detalle d on o.orden_id = d.orden_id