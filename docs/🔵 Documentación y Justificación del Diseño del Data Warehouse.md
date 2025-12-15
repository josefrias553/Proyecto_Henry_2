# 📘 Documentación y Justificación del Diseño del Data Warehouse

## 🏗️ Arquitectura del Sistema

### Separación OLTP vs OLAP

El proyecto implementa una **arquitectura de dos esquemas** para separar las operaciones transaccionales de las analíticas:

#### **Esquema `public` - OLTP (Operational Database)**
- **Propósito**: Base de datos operacional para transacciones del e-commerce
- **Tablas**: `usuarios`, `productos`, `ordenes`, `detalleordenes`, `categorias`, `direccionesenvio`, `metodospago`, `historialpagos`, `resenasproductos`, `carrito`, `ordenesmetodospago`
- **Características**: 
  - Normalizada (3NF) para evitar redundancia
  - Optimizada para operaciones CRUD (Create, Read, Update, Delete)
  - Datos en tiempo real
  - Alta frecuencia de escrituras

#### **Esquema `dw` - OLAP (Analytical Database)**
- **Propósito**: Data Warehouse para análisis y reportería
- **Tablas**: Dimensiones (`dim_*`) y Hechos (`fact_*`)
- **Características**:
  - Desnormalizada (Star Schema) para optimizar consultas analíticas
  - Optimizada para lectura y agregaciones
  - Actualizada mediante procesos ETL/ELT
  - Historial y versionado (SCD2)

### Pipeline de Transformación

El flujo de datos sigue una arquitectura **ELT (Extract, Load, Transform)** implementada con dbt:

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Fuentes   │ --> │ Python       │ --> │ dbt          │ --> │ Data         │
│   Raw Data  │     │ Loaders      │     │ Transforms   │     │ Warehouse    │
│  (CSV/JSON) │     │ (schema      │     │ (3 capas)    │     │ (schema dw)  │
│             │     │  public)     │     │              │     │              │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                           ↓                     ↓                     ↓
                        EXTRACT              TRANSFORM              LOAD
                         LOAD                                     (to dw)
```

#### **Capa 1: Staging** (`dbt_ecommerce_dw/models/staging/`)
- **Fuente**: Tablas del esquema `public`
- **Propósito**: 
  - Vista 1:1 de las tablas fuente
  - Conversión de tipos de datos
  - Renombrado de columnas a convenciones consistentes
  - Limpieza básica (nulls, duplicados)
- **Nomenclatura**: `stg_<table_name>`

#### **Capa 2: Intermediate** (`dbt_ecommerce_dw/models/intermediate/`)
- **Fuente**: Modelos de staging
- **Propósito**:
  - Joins lógicos entre tablas
  - Cálculos de métricas derivadas
  - Aplicación de reglas de negocio
  - Agregaciones intermedias
- **Nomenclatura**: `int_<business_concept>`

#### **Capa 3: Mart** (`dbt_ecommerce_dw/models/mart/`)
- **Fuente**: Modelos intermediate
- **Propósito**:
  - **Dimensiones**: Tablas de contexto con SCD (Slowly Changing Dimensions)
  - **Hechos**: Tablas de eventos medibles con métricas cuantitativas
  - Modelo dimensional final (Star Schema)
- **Destino**: Esquema `dw`
- **Nomenclatura**: `dim_*` (dimensiones), `fact_*` (hechos)

---

## 🎯 Enfoque Metodológico
El modelo se diseñó siguiendo la metodología **Kimball**, que propone un esquema en estrella donde:
- Las **tablas de hechos** capturan eventos medibles del negocio.
- Las **dimensiones** permiten filtrar, segmentar y contextualizar esos hechos.

El objetivo central fue responder preguntas de negocio clave relacionadas con **ventas**, **pagos**, **usuarios**, **productos** y **stock**.

---

## 🛒 Hechos Seleccionados
Cada tabla de hechos se definió con un **grain** (nivel de detalle) claro y específico:

### **fact_order** (nivel orden)
**Grain**: Una fila por orden de compra.

**Columnas en dbt**:
- `order_sk` (Surrogate Key) - Hash MD5 de order_id
- `order_id` (Degenerate Dimension)
- `customer_sk` (FK a dim_customer)
- `date_sk` (FK a dim_time)
- `order_status_sk` (FK a dim_order_status)
- `total_amount` (total de la orden) - **MEDIDA ADITIVA**
- `item_count` (cantidad de ítems únicos) - **MEDIDA SEMI-ADITIVA**
- `total_quantity` (cantidad total de productos) - **MEDIDA ADITIVA**
- `created_at` (timestamp de creación)
- `updated_at` (timestamp de actualización)

**Justificación**: Permite medir ticket promedio, cantidad de órdenes y variación mensual.

---

### **fact_order_line** (nivel ítem)
**Grain**: Una fila por producto dentro de una orden (línea de pedido).

**Columnas en dbt**:
- `order_line_sk` (Surrogate Key) - Hash MD5 de detalle_id
- `order_id` (Degenerate Dimension)
- `order_sk` (FK a fact_order) - Para navegación a nivel orden
- `customer_sk` (FK a dim_customer)
- `product_sk` (FK a dim_product)
- `date_sk` (FK a dim_time)
- `quantity` (cantidad del producto) - **MEDIDA ADITIVA**
- `price_unit` (precio unitario) - **MEDIDA NO-ADITIVA**
- `total` (quantity × price_unit) - **MEDIDA ADITIVA**
- `created_at`
- `updated_at`

**Justificación**: Habilita análisis de productos más vendidos, volumen por categoría y ventas por día a nivel granular.

---

### **fact_payment**
**Grain**: Una fila por transacción de pago asociada a una orden.

**Columnas en dbt**:
- `payment_sk` (Surrogate Key) - Hash MD5 de payment_id
- `payment_id` (Degenerate Dimension)
- `order_id` (Degenerate Dimension)
- `order_sk` (FK a fact_order)
- `payment_method_sk` (FK a dim_payment_method)
- `date_sk` (FK a dim_time)
- `amount` (monto pagado) - **MEDIDA ADITIVA**
- `state_code` (estado del pago: Procesando, Completado, Fallido)
- `created_at`

**Justificación**: Responde preguntas sobre métodos de pago, montos promedio y pagos fallidos o en proceso.

---

### **fact_inventory_snapshot**
**Grain**: Snapshot diario de stock por producto (Periodic Snapshot).

**Columnas en dbt**:
- `inventory_sk` (Surrogate Key)
- `product_sk` (FK a dim_product)
- `date_sk` (FK a dim_time)
- `stock` (unidades disponibles) - **MEDIDA SEMI-ADITIVA** (no aditiva en tiempo)
- `stock_reserved` (unidades reservadas) - **MEDIDA SEMI-ADITIVA**
- `avg_cost` (costo promedio) - **MEDIDA NO-ADITIVA**
- `created_at`

**Justificación**: Permite analizar disponibilidad, faltantes y la relación stock vs ventas en un punto específico del tiempo.

---

### **fact_order_accum**
**Grain**: Una fila por orden, acumulando fechas clave del ciclo de vida (Accumulating Snapshot).

**Columnas en dbt**:
- `order_sk` (FK a fact_order)
- `order_id` (Degenerate Dimension)
- `date_sk` (FK a dim_time) - Fecha de la orden
- `order_status_sk` (FK a dim_order_status)

**Nota**: Este modelo está preparado para agregar más fechas milestone (fecha_pago, fecha_envío, fecha_entrega) en el futuro.

**Justificación**: Mide tiempos de procesamiento, envío y entrega cuando se implementen los milestones adicionales.

---

### **fact_ventas_agg_daily**
**Grain**: Agregado diario por producto y categoría (Aggregate Fact Table).

**Columnas en dbt**:
- `agg_id` (Surrogate Key - Secuencial)
- `date_sk` (FK a dim_time)
- `product_sk` (FK a dim_product)
- `category_sk` (FK a dim_category)
- `total_quantity` (cantidad total vendida) - **MEDIDA ADITIVA**
- `total_revenue` (ingresos totales) - **MEDIDA ADITIVA**
- `order_count` (número de órdenes) - **MEDIDA ADITIVA**

**Justificación**: Optimiza consultas sobre ingresos y volumen por día para análisis de alto nivel y reportes agregados.

> **Cada hecho fue elegido porque representa un evento medible directamente asociado a una pregunta de negocio. Los grains fueron diseñados para soportar diferentes niveles de análisis: orden completo, línea de producto, pago individual, inventario diario y agregados pre-calculados.**

---

## 👤 **Dimensiones y Estrategia SCD**
Las dimensiones se diseñaron para permitir análisis flexibles en múltiples ejes. Se aplicaron estrategias de **Slowly Changing Dimensions (SCD)** de acuerdo con la naturaleza de cada dimensión:

### **dim_customer — SCD2**
**Columnas en dbt**:
- `customer_sk` (Surrogate Key) - Generado con hash MD5 de customer_id
- `customer_id` (Natural Key)
- `first_name` (nombre)
- `last_name` (apellido)  
- `email`
- `created_at` (fecha_registro)
- `segment_sk` (FK a dim_customer_segment)
- `current_flag` - Indica registro activo
- `valid_from` (eff_from) - Timestamp de inicio de vigencia
- `valid_to` (eff_to) - Timestamp de fin de vigencia

**Justificación**: Cambian atributos como email o segmento. Se requiere historial para análisis de comportamiento y fidelidad.

---

### **dim_product — SCD2 parcial**
**Columnas en dbt**:
- `product_sk` (Surrogate Key) - Generado con hash MD5 de product_id
- `product_id` (Natural Key)
- `name` (nombre del producto)
- `description` (descripción)
- `category_id` (FK)
- `category_name` 
- `current_price` (precio actual)
- `current_flag` - Indica versión activa
- `valid_from` (eff_from)
- `valid_to` (eff_to)

**Justificación**: Cambian precio y categoría. Se conserva historial de precios para análisis de rentabilidad histórica.

---

### **dim_address — SCD2**
**Columnas en dbt**:
- `address_sk` (Surrogate Key) - Generado con hash MD5 de address_id
- `address_id` (Natural Key)
- `customer_id` (usuario_id)
- `street` (calle)
- `city` (ciudad)
- `state` (provincia)
- `country` (país)
- `postal_code` (código postal)
- `current_flag` - Indica dirección activa
- `valid_from` (eff_from)
- `valid_to` (eff_to)

**Justificación**: Las direcciones cambian con frecuencia. Necesario preservar la dirección vigente al momento del envío.

---

### **dim_category — SCD1**
**Columnas en dbt**:
- `category_sk` (Surrogate Key) - Generado con hash MD5 de category_id
- `category_id` (Natural Key)
- `name` (nombre de la categoría)
- `description` (descripción)

**Justificación**: Catálogo relativamente estático. Cambios se sobrescriben sin historial.

---

### **dim_customer_segment — Mini-Dimensión (SCD1)**
**Columnas en dbt**:
- `segment_sk` (Surrogate Key) - Generado con hash MD5 de customer_id + segment_code
- `customer_id` 
- `segment_code` - Código del segmento (LOYAL, ACTIVE, NEW)
- `segment_name` - Nombre descriptivo del segmento
- `loyalty_tier` - Nivel de lealtad (Gold, Silver, Bronze)
- `risk_score` - Score de riesgo (0.05 para LOYAL, 0.15 para ACTIVE, 0.30 para NEW)
- `last_behavior_flag` - Flag de último comportamiento
- `description` - Descripción del segmento

**Lógica de Segmentación** (implementada en `int_customer_segment`):
- **LOYAL**: Clientes registrados hace más de 2 años
- **ACTIVE**: Clientes registrados hace más de 6 meses  
- **NEW**: Clientes registrados hace menos de 6 meses

**Justificación**: Cambios no requieren historial. Reglas de segmentación se sobrescriben.

---

### **dim_payment_method — SCD1**
**Columnas en dbt**:
- `payment_method_sk` (Surrogate Key)
- `payment_method_id` (Natural Key)
- `name` (nombre del método)
- `description` (descripción)

**Justificación**: Métodos de pago son estáticos. Suficiente con sobrescribir cambios.

---

### **dim_order_status — SCD1**
**Columnas en dbt**:
- `order_status_sk` (Surrogate Key)
- `status_code` (código del estado)
- `description` (descripción del estado)

**Justificación**: Estados del flujo transaccional no requieren versiones históricas.

---

### **dim_review — SCD1 (Tabla de Referencia)**
**Columnas en dbt**:
- `review_id` (Natural Key)
- `product_id` (FK a dim_product)
- `customer_id` (FK a dim_customer)
- `rating` (calificación 1-5)
- `comment_length` (longitud del comentario)
- `review_date` (fecha de la reseña)

**Nota**: Implementado como **incremental** con `unique_key='review_id'`.

**Justificación**: Cada reseña es un evento único y no se actualiza. Se agrega como referencia dimensional.

---

### **dim_time — Pre-Calculada**
**Columnas en dbt**:
- `date_sk` (Surrogate Key) - Formato YYYYMMDD como integer
- `date_value` (Natural Key) - Fecha real
- `year` - Año calendario
- `month` - Mes calendario (1-12)
- `day` - Día del mes (1-31)
- `weekday` - Día de la semana (1-7, donde 1=Domingo)
- `is_weekend` - Boolean (TRUE para Sábado y Domingo)
- `is_holiday` - Boolean (actualmente FALSE, preparado para futura configuración)
- `fiscal_week` - Semana fiscal
- `fiscal_month` - Mes fiscal
- `fiscal_year` - Año fiscal

**Rango**: 2015-01-01 a 2030-12-31 (generado con `dbt_utils.date_spine`)

**Justificación**: Dimensión pre-calculada para optimizar joins temporales y análisis por períodos.

---

## 🔗 Relaciones
- Cada tabla de hechos se conecta a sus dimensiones mediante **surrogate keys** (`*_sk`).
- Las relaciones son **1:N**, donde una dimensión describe múltiples registros en una tabla de hechos.

Ejemplos:
- Un cliente en **dim_customer** puede tener muchas órdenes en **fact_order**.
- Un producto en **dim_product** puede aparecer en múltiples líneas de **fact_order_line**.

---

## ✅ Conclusión
Las decisiones de diseño se tomaron para garantizar:

- Granularidad precisa en cada tabla de hechos.  
- Conservación del historial en dimensiones críticas mediante SCD2.  
- Optimización de consultas analíticas con snapshots y agregados diarios.  
- Simplicidad y performance en dimensiones estáticas mediante SCD1.  

El resultado es un **modelo lógico robusto, escalable y alineado a las preguntas de negocio**, permitiendo análisis confiables y eficientes.
