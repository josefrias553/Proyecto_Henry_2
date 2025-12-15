with ordenes_metodos as (
    select * from {{ ref('stg_ordenesmetodospago') }}
),
metodos as (
    select * from {{ ref('stg_metodospago') }}
)
select
    om.orden_metodo_id,
    om.orden_id,
    om.metodo_pago_id,
    m.nombre as metodo_nombre,
    m.descripcion as metodo_descripcion,
    om.monto_pagado
from ordenes_metodos om
left join metodos m on om.metodo_pago_id = m.metodo_pago_id