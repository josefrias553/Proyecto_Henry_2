# 📊 Preguntas de Análisis de Datos – E-commerce

## 🏗️ Arquitectura del Sistema

### Diseño de Dos Esquemas

El proyecto utiliza una arquitectura moderna que separa las operaciones transaccionales (OLTP) de las analíticas (OLAP):

**Esquema `public`** - **Base de Datos Operacional (OLTP)**
- Contiene las tablas transaccionales del e-commerce
- Tablas: `usuarios`, `productos`, `ordenes`, `detalleordenes`, `categorias`, `direccionesenvio`, `metodospago`, `historialpagos`, `resenasproductos`, `carrito`
- Normalizada (3NF) para eficiencia operacional
- Gestionada por Python loaders que extraen datos de fuentes raw (CSV/JSON)

**Esquema `dw`** - **Data Warehouse (OLAP)**
- Contiene el modelo dimensional optimizado para análisis
- Tablas de dimensiones (`dim_*`) y hechos (`fact_*`)
- Desnormalizada (Star Schema) para consultas rápidas
- Generada por dbt a través de transformaciones en 3 capas:
  1. **Staging**: Normalización desde esquema `public`
  2. **Intermediate**: Lógica de negocio y agregaciones
  3. **Mart**: Modelos dimensionales finales en esquema `dw`

### Flujo de Datos

```
Fuentes Raw (CSV/JSON)
        ↓
Python Loaders → Esquema 'public' (ODS)
        ↓
dbt Staging → Limpieza y normalización
        ↓
dbt Intermediate → Lógica de negocio
        ↓
dbt Mart → Esquema 'dw' (Star Schema)
        ↓
Herramientas BI (PowerBI, Tableau, Metabase)
```

---

## 🛒 **Ventas**
- ¿Cuáles son los productos más vendidos por volumen?  
- ¿Cuál es el ticket promedio por orden?  
- ¿Cuáles son las categorías con mayor número de productos vendidos?  
- ¿Qué día de la semana se generan más ventas?  
- ¿Cuántas órdenes por mes se generan y cuál es su variación mensual?  

---

## 💳 **Pagos y Transacciones**
- ¿Cuáles son los métodos de pago más utilizados?  
- ¿Cuál es el monto promedio pagado por método de pago?  
- ¿Cuántas órdenes se pagaron usando más de un método de pago?  
- ¿Cuántos pagos están en estado “Procesando” o “Fallido”?  
- ¿Cuál es el monto total recaudado por mes?  

---

## 👤 **Usuarios**
- ¿Cuántos usuarios se registran por mes?  
- ¿Cuántos usuarios han realizado más de una orden?  
- ¿Cuántos usuarios registrados no han hecho ninguna compra?  
- ¿Qué usuarios han gastado más en total?  
- ¿Cuántos usuarios han dejado reseñas?  

---

## 📦 **Productos y Stock**
- ¿Qué productos tienen alto stock pero bajas ventas?  
- ¿Cuántos productos están actualmente fuera de stock?  
- ¿Cuáles son los productos peor calificados?  
- ¿Qué productos tienen mayor cantidad de reseñas?  
- ¿Qué categoría tiene el mayor valor económico vendido (no solo volumen)?

# 🧮 **Medidas y 📐 Dimensiones por Área de Análisis**

## ✅ **Ventas**
**Medidas:**
- cantidad  
- precio_unitario  
- total
- **ticket_promedio = SUM(total_orden) / COUNT(order_id)**  
- ventas_volumen  
- **ventas_valor = cantidad * precio_unitario**

**Dimensiones:**
- dim_producto  
- dim_categoria  
- dim_cliente  
- dim_tiempo (día, mes, weekday)  
- dim_direccion (ciudad, provincia)  
- dim_estado_orden  

---

## 💳 **Pagos y Transacciones**
**Medidas:**
- monto_pago  
- monto_promedio_por_metodo  
- numero_metodos_por_orden  
- cantidad_pagos_procesando  
- cantidad_pagos_fallidos  
- monto_total_mes  

**Dimensiones:**
- dim_metodo_pago  
- dim_tiempo  
- dim_orden *(degenerate: order_id)*  

---

## 👤 **Usuarios**
**Medidas:**
- numero_registros_por_mes  
- numero_ordenes_por_usuario  
- gasto_total_por_usuario  
- cantidad_reseñas  
- usuarios_sin_compra *(derivada)*  

**Dimensiones:**
- dim_cliente  
- dim_tiempo *(fecha_registro)*  
- dim_segmento_cliente *(mini-dim)*  

---

## 📦 **Productos y Stock**
**Medidas:**
- stock_actual  
- stock_reservado  
- ventas_volumen  
- ventas_valor  
- numero_reseñas  
- rating_promedio  

**Dimensiones:**
- dim_producto  
- dim_categoria  
- dim_tiempo

# 📐 **Esquema Conceptual del Modelo Dimensional**

![Conceptual.png](../img/Conceptual.png)

# 📐 **Esquema Logico del Modelo Dimensional**

![Logico.png](../img/Logico.png)

# 🧩 **Entidades del Modelo Dimensional**

## 🔹 **Dimensiones**
Lista de dimensiones incluidas en el Data Warehouse, con su estrategia SCD cuando aplica:

- **dim_customer** — cliente *(SCD2)*
- **dim_product** — producto *(SCD2 parcial)*
- **dim_category** — categoría de producto
- **dim_address** — dirección de envío *(SCD2)*
- **dim_time** — calendario (día, mes, año, fiscal)
- **dim_payment_method** — método de pago
- **dim_order_status** — estado de la orden
- **dim_customer_segment** — segmento del cliente *(mini-dim)*
- **dim_review** — reseña *(puede ser dimensión o hecho)*

---

## 🔸 **Hechos**
Tablas de hechos definidas según el tipo de evento de negocio:

- **fact_order** — orden *(nivel orden)*
- **fact_order_line** — ítem dentro de una orden *(nivel línea)*
- **fact_payment** — pagos por transacción
- **fact_inventory_snapshot** — stock diario por producto
- **fact_order_accum** — ciclo de vida de la orden *(accumulating snapshot)*
- **fact_ventas_agg_daily** — agregados diarios × producto × categoría


# 🔗 Relaciones y Cardinalidades

| Relación                                           | Cardinalidad | Descripción                                         |
|----------------------------------------------------|--------------|-----------------------------------------------------|
| dim_customer (1) ↔ fact_order (N)                  | 1:N          | Un cliente puede tener muchas órdenes               |
| dim_customer (1) ↔ fact_order_line (N)             | 1:N          | Un cliente puede tener muchas líneas de pedido      |
| dim_customer (1) ↔ dim_review (N)                  | 1:N          | Un cliente puede dejar muchas reseñas               |
| dim_product (1) ↔ fact_order_line (N)              | 1:N          | Un producto puede aparecer en muchas líneas         |
| dim_product (1) ↔ dim_review (N)                   | 1:N          | Un producto puede tener muchas reseñas              |
| dim_product (1) ↔ fact_inventory_snapshot (N)      | 1:N          | Un producto tiene múltiples snapshots diarios       |
| dim_category (1) ↔ dim_product (N)                 | 1:N          | Una categoría agrupa muchos productos               |
| dim_address (1) ↔ fact_order (N)                   | 1:N          | Una dirección puede estar asociada a muchas órdenes |
| dim_address (1) ↔ fact_order_line (N)              | 1:N          | Una dirección puede estar asociada a muchas líneas  |
| dim_time (1) ↔ fact_order (N)                      | 1:N          | Una fecha puede tener muchas órdenes                |
| dim_time (1) ↔ fact_order_line (N)                 | 1:N          | Una fecha puede tener muchas líneas                 |
| dim_time (1) ↔ fact_payment (N)                    | 1:N          | Una fecha puede tener muchos pagos                  |
| dim_time (1) ↔ fact_inventory_snapshot (N)         | 1:N          | Una fecha puede tener muchos snapshots              |
| dim_payment_method (1) ↔ fact_payment (N)          | 1:N          | Un método puede usarse en muchos pagos              |
| dim_order_status (1) ↔ fact_order (N)              | 1:N          | Un estado puede aplicarse a muchas órdenes          |
| dim_order_status (1) ↔ fact_order_accum (N)        | 1:N          | Un estado puede aplicarse a órdenes acumuladas      |
| dim_customer_segment (1) ↔ dim_customer (N)        | 1:N          | Un segmento puede agrupar muchos clientes           |

# 📊 **Hechos Centrales y Medidas Cuantitativas**

## 🛒 **Ventas**
**Tabla de hechos:** `fact_order_line`
**Grain:** Una fila por producto dentro de una orden (línea de pedido)

**Medidas implementadas en dbt:**
- `quantity` (Integer) - Cantidad de productos vendidos - **ADITIVA**
- `price_unit` (Numeric) - Precio unitario - **NO-ADITIVA**
- `total` (Numeric) - Ingreso por línea (quantity × price_unit) - **ADITIVA**

**Foreign Keys:**
- `order_line_sk` - Surrogate key
- `order_id` - Degenerate dimension
- `order_sk` - FK a fact_order
- `customer_sk` - FK a dim_customer
- `product_sk` - FK a dim_product
- `date_sk` - FK a dim_time

---

## 📦 **Órdenes**
**Tabla de hechos:** `fact_order`
**Grain:** Una fila por orden de compra

**Medidas implementadas en dbt:**
- `total_amount` (Numeric) - Monto total de la orden - **ADITIVA**
- `item_count` (Integer) - Cantidad de ítems únicos por orden - **SEMI-ADITIVA**
- `total_quantity` (Integer) - Cantidad total de productos - **ADITIVA**

**Foreign Keys:**
- `order_sk` - Surrogate key
- `order_id` - Degenerate dimension
- `customer_sk` - FK a dim_customer
- `date_sk` - FK a dim_time
- `order_status_sk` - FK a dim_order_status

---

## 💳 **Pagos**
**Tabla de hechos:** `fact_payment`
**Grain:** Una fila por transacción de pago

**Medidas implementadas en dbt:**
- `amount` (Numeric) - Monto pagado - **ADITIVA**
- `state_code` (String) - Estado del pago (Procesando, Completado, Fallido)

**Foreign Keys:**
- `payment_sk` - Surrogate key
- `payment_id` - Degenerate dimension
- `order_id` - Degenerate dimension
- `order_sk` - FK a fact_order
- `payment_method_sk` - FK a dim_payment_method
- `date_sk` - FK a dim_time

---

## 📦 **Stock**
**Tabla de hechos:** `fact_inventory_snapshot`
**Grain:** Snapshot diario de inventario por producto (Periodic Snapshot)

**Medidas implementadas en dbt:**
- `stock` (Integer) - Unidades disponibles - **SEMI-ADITIVA** (no aditiva en tiempo)
- `stock_reserved` (Integer) - Unidades reservadas - **SEMI-ADITIVA**
- `avg_cost` (Numeric) - Costo promedio del producto - **NO-ADITIVA**

**Foreign Keys:**
- `inventory_sk` - Surrogate key
- `product_sk` - FK a dim_product
- `date_sk` - FK a dim_time

---

## 📈 **Ventas agregadas**
**Tabla de hechos:** `fact_ventas_agg_daily`
**Grain:** Agregado diario por producto y categoría (Aggregate Fact Table)

**Medidas implementadas en dbt:**
- `total_quantity` (Integer) - Unidades vendidas por día - **ADITIVA**
- `total_revenue` (Numeric) - Ingresos totales por día - **ADITIVA**
- `order_count` (Integer) - Cantidad de órdenes por día - **ADITIVA**

**Foreign Keys:**
- `agg_id` - Surrogate key secuencial
- `date_sk` - FK a dim_time
- `product_sk` - FK a dim_product
- `category_sk` - FK a dim_category

---

## 📝 **Reseñas**
**Tabla de dimensión/hecho:** `dim_review`
**Grain:** Una fila por reseña (evento único)

**Atributos y Medidas:**
- `rating` (Integer) - Puntuación del producto (1-5)
- `comment_length` (Integer) - Longitud del comentario  
- `review_date` (Date) - Fecha de la reseña

**Referencias:**
- `review_id` - Natural key
- `product_id` - FK a dim_product
- `customer_id` - FK a dim_customer

**Nota:** Implementado como **incremental** para eficiencia en la carga.

# 📐 **Dimensiones Analíticas – DW E-Commerce**

## ⏱️ **dim_time**
**Propósito:** agrupar por fecha, mes, año, día de la semana y calendario fiscal.

**Atributos implementados en dbt:**
- `date_sk` (Integer) - Surrogate key en formato YYYYMMDD
- `date_value` (Date) - Fecha real (Natural Key) 
- `year` (Integer) - Año calendario
- `month` (Integer) - Mes calendario (1-12)
- `day` (Integer) - Día del mes (1-31)
- `weekday` (Integer) - Día de la semana (1-7, donde 1=Domingo)
- `is_weekend` (Boolean) - TRUE para Sábado (6) y Domingo (0)
- `is_holiday` (Boolean) - Preparado para configuración futura (actualmente FALSE)
- `fiscal_week` (Integer) - Semana del año
- `fiscal_month` (Integer) - Mes fiscal
- `fiscal_year` (Integer) - Año fiscal

**Rango de datos**: 2015-01-01 a 2030-12-31 (generado con `dbt_utils.date_spine`)

✅ Permite análisis por períodos, estacionalidad, días hábiles y calendario fiscal.

---

## 👤 **dim_customer**
**Propósito:** segmentar por cliente, comportamiento, antigüedad y segmento.

**Atributos implementados en dbt:**
- `customer_sk` (String) - Surrogate key generado con MD5 hash
- `customer_id` (Integer) - Natural key
- `first_name` (String) - Nombre del cliente
- `last_name` (String) - Apellido del cliente
- `email` (String) - Email único
- `created_at` (Timestamp) - Fecha de registro (fecha_registro)
- `segment_sk` (String) - FK a dim_customer_segment
- `current_flag` (Boolean) - Indica versión actual (SCD2)
- `valid_from` (Timestamp) - Inicio de vigencia (eff_from)
- `valid_to` (Timestamp) - Fin de vigencia (eff_to)

**Estrategia SCD**: SCD2 completo con versionado histórico

✅ Permite análisis de clientes activos/inactivos, fidelización, antigüedad y segmentación.

---

## 🧩 **dim_customer_segment**
**Propósito:** agrupar clientes por perfil, antigüedad, riesgo y lealtad.

**Atributos implementados en dbt:**
- `segment_sk` (String) - Surrogate key (hash de customer_id + segment_code)
- `customer_id` (Integer) - Referencia al cliente
- `segment_code` (String) - Código del segmento: LOYAL, ACTIVE, NEW
- `segment_name` (String) - Nombre descriptivo:
  - 'Cliente leal' (LOYAL)
  - 'Cliente activo' (ACTIVE)
  - 'Cliente nuevo' (NEW)
- `loyalty_tier` (String) - Nivel de lealtad:
  - 'Gold' (LOYAL)
  - 'Silver' (ACTIVE)
  - 'Bronze' (NEW)
- `risk_score` (Numeric) - Score de riesgo:
  - 0.05 (LOYAL - bajo riesgo)
  - 0.15 (ACTIVE - riesgo medio)
  - 0.30 (NEW - alto riesgo)
- `last_behavior_flag` (Boolean) - TRUE solo para LOYAL
- `description` (String) - "Segmento derivado por antigüedad"

**Lógica de segmentación** (calculada en `int_customer_segment`):
- **LOYAL**: registrados hace más de 2 años
- **ACTIVE**: registrados hace más de 6 meses
- **NEW**: registrados hace menos de 6 meses

✅ Habilita segmentación avanzada por comportamiento y perfil de riesgo.

---

## 📦 **dim_product**
**Propósito:** filtrar por producto, categoría, precio y estado.

**Atributos implementados en dbt:**
- `product_sk` (String) - Surrogate key (MD5 hash de producto_id)
- `product_id` (Integer) - Natural key
- `name` (String) - Nombre del producto
- `description` (Text) - Descripción del producto
- `category_id` (Integer) - FK a categoría
- `category_name` (String) - Nombre de la categoría (desnormalizado)
- `current_price` (Numeric) - Precio actual del producto
- `current_flag` (Boolean) - Indica versión actual (SCD2)
- `valid_from` (Timestamp) - Inicio de vigencia
- `valid_to` (Timestamp) - Fin de vigencia

**Estrategia SCD**: SCD2 parcial para historial de precios

✅ Facilita análisis por categoría, productos vigentes, precios y evolución histórica.

---

## 🗂️ **dim_category**
**Propósito:** agrupar productos por categoría.

**Atributos implementados en dbt:**
- `category_sk` (String) - Surrogate key (MD5 hash de categoria_id)
- `category_id` (Integer) - Natural key
- `name` (String) - Nombre de la categoría
- `description` (String) - Descripción de la categoría

**Estrategia SCD**: SCD1 (sobrescritura simple)

✅ Permite análisis por categoría principal.

---

## 🏠 **dim_address**
**Propósito:** segmentar por ubicación geográfica.

**Atributos implementados en dbt:**
- `address_sk` (String) - Surrogate key (MD5 hash de direccion_id)
- `address_id` (Integer) - Natural key
- `customer_id` (Integer) - ID del cliente (usuario_id)
- `street` (String) - Calle (calle)
- `city` (String) - Ciudad (ciudad)
- `state` (String) - Provincia/Estado (provincia)
- `country` (String) - País (pais)
- `postal_code` (String) - Código postal (codigo_postal)
- `current_flag` (Boolean) - Indica dirección activa (SCD2)
- `valid_from` (Timestamp) - Inicio de vigencia
- `valid_to` (Timestamp) - Fin de vigencia

**Estrategia SCD**: SCD2 para preservar historial de direcciones

✅ Permite análisis por región, país, ciudad y cambios de domicilio.

---

## 💳 **dim_payment_method**
**Propósito:** agrupar por método de pago.

**Atributos implementados en dbt:**
- `payment_method_sk` (String) - Surrogate key
- `payment_method_id` (Integer) - Natural key
- `name` (String) - Nombre del método de pago
- `description` (String) - Descripción del método

**Estrategia SCD**: SCD1 (catálogo estático)

✅ Permite análisis por tipo de pago (tarjeta, transferencia, efectivo, etc.).

---

## 📦 **dim_order_status**
**Propósito:** filtrar por estado de la orden.

**Atributos implementados en dbt:**
- `order_status_sk` (String) - Surrogate key
- `status_code` (String) - Código del estado (pendiente, enviado, completado, etc.)
- `description` (String) - Descripción del estado

**Estrategia SCD**: SCD1 (catálogo estático)

✅ Permite análisis por estado (pendiente, enviado, completado, cancelado).

---

## 📝 **dim_review**
**Propósito:** segmentar y analizar reseñas y calificaciones.

**Atributos implementados en dbt:**
- `review_id` (Integer) - Natural key (resena_id)
- `product_id` (Integer) - FK a dim_product
- `customer_id` (Integer) - FK a dim_customer
- `rating` (Integer) - Calificación 1-5 (calificacion)
- `comment_length` (Integer) - Longitud del comentario
- `review_date` (Date) - Fecha de la reseña

**Materialización**: Incremental con `unique_key='review_id'`

**Estrategia SCD**: SCD1 (reseñas no se modifican)

✅ Permite análisis de calidad percibida, volumen de reseñas y comportamiento del cliente.

# 📐 **Estrategia SCD**

## 🧬 **Tipo 2 (SCD2)**
Aplicado cuando es necesario conservar historial completo de cambios.

**Dimensiones:**
- `dim_customer`
- `dim_product` *(parcial)*
- `dim_address`
- `dim_category` *(si se requiere historial completo)*

**Cuándo usarlo:**
- Cuando los cambios deben reflejar el estado exacto al momento de la transacción.
- Para análisis históricos, seguimiento de evolución y auditoría.

---

## 🧩 **Tipo 1 (SCD1)**
Aplicado cuando no es necesario mantener versiones históricas.

**Dimensiones:**
- `dim_customer_segment`
- `dim_payment_method`
- `dim_order_status`
- `dim_review`

**Cuándo usarlo:**
- Cuando son catálogos estáticos.
- Cuando los cambios no afectan el análisis histórico.

---

## 🎯 **Justificación general**
Se aplica **SCD2** en dimensiones críticas donde los cambios deben preservarse (clientes, productos, direcciones), permitiendo análisis históricos precisos.  
Se utiliza **SCD1** en dimensiones estables o donde sobrescribir es suficiente, optimizando simplicidad y mantenimiento.



