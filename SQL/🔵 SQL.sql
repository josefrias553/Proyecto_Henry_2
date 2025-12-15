-- ==========================================
-- 📊 DATA WAREHOUSE - ESQUEMA DIMENSIONAL
-- ==========================================
-- 
-- PROPÓSITO:
-- Este script crea la estructura completa del Data Warehouse (OLAP) 
-- para el sistema de e-commerce en el esquema 'dw'.
--
-- ARQUITECTURA:
-- El proyecto utiliza una arquitectura de dos esquemas:
--   • ESQUEMA 'public': Tablas transaccionales OLTP (Operational Database)
--                       Contiene: usuarios, productos, ordenes, pagos, etc.
--   • ESQUEMA 'dw':     Data Warehouse OLAP (Analytical Database)
--                       Contiene: dimensiones (dim_*) y hechos (fact_*)
--
-- FLUJO DE DATOS:
-- 1. Python loaders → Cargan datos raw al esquema 'public' (ODS)
-- 2. dbt (Staging)   → Normaliza datos desde 'public'
-- 3. dbt (Intermediate) → Aplica lógica de negocio
-- 4. dbt (Mart)      → Genera tablas dimensionales en esquema 'dw'
--
-- MODELO DIMENSIONAL:
-- Esquema Estrella (Star Schema) con:
--   • 9 Dimensiones: customer, product, category, address, time,
--                    payment_method, order_status, customer_segment, review
--   • 6 Hechos: fact_order, fact_order_line, fact_payment,
--               fact_inventory_snapshot, fact_order_accum, fact_ventas_agg_daily
--
-- ESTRATEGIA SCD:
--   • SCD2: dim_customer, dim_product, dim_address (historial completo)
--   • SCD1: dim_category, dim_payment_method, dim_order_status, etc.
-- ==========================================

CREATE SCHEMA IF NOT EXISTS dw;
SET search_path = dw, public;

CREATE TABLE dw.dim_time (
    date_sk        INTEGER PRIMARY KEY,
    date_value     DATE        NOT NULL,
    year           INTEGER     NOT NULL,
    month          INTEGER     NOT NULL,
    day            INTEGER     NOT NULL,
    weekday        INTEGER     NOT NULL,
    is_weekend     BOOLEAN     DEFAULT FALSE,
    is_holiday     BOOLEAN     DEFAULT FALSE,
    fiscal_week    INTEGER,
    fiscal_month   INTEGER,
    fiscal_year    INTEGER
);

CREATE INDEX idx_dim_time_date_value ON dw.dim_time(date_value);

CREATE TABLE dw.dim_customer (
    customer_sk    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id    TEXT        NOT NULL,
    nombre         TEXT,
    apellido       TEXT,
    email          TEXT,
    fecha_registro DATE,
    segment_sk     BIGINT,
    current_flag   BOOLEAN     DEFAULT TRUE,
    eff_from       TIMESTAMP   DEFAULT now(),
    eff_to         TIMESTAMP,
    notes          TEXT
);

CREATE UNIQUE INDEX ux_dim_customer_customer_id_current
    ON dw.dim_customer(customer_id, current_flag)
    WHERE current_flag IS TRUE;

CREATE INDEX idx_dim_customer_segment_sk ON dw.dim_customer(segment_sk);

CREATE TABLE dw.dim_customer_segment (
    segment_sk     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    segment_code   TEXT,
    segment_name   TEXT,
    loyalty_tier   TEXT,
    risk_score     NUMERIC(6,2),
    last_behavior_flag BOOLEAN,
    description    TEXT
);

CREATE TABLE dw.dim_product (
    product_sk     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id     TEXT        NOT NULL,
    name           TEXT,
    description    TEXT,
    category_sk    BIGINT,
    active_flag    BOOLEAN     DEFAULT TRUE,
    current_price  NUMERIC(18,2),
    current_flag   BOOLEAN     DEFAULT TRUE,
    eff_from       TIMESTAMP   DEFAULT now(),
    eff_to         TIMESTAMP
);

CREATE UNIQUE INDEX ux_dim_product_product_id_current
    ON dw.dim_product(product_id, current_flag)
    WHERE current_flag IS TRUE;

CREATE INDEX idx_dim_product_category_sk ON dw.dim_product(category_sk);

CREATE TABLE dw.dim_category (
    category_sk    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_id    INTEGER,
    name           TEXT
);

CREATE TABLE dw.dim_address (
    address_sk     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    address_id     TEXT,
    usuario_id     TEXT,
    calle          TEXT,
    ciudad         TEXT,
    provincia      TEXT,
    pais           TEXT,
    postal_code    TEXT,
    current_flag   BOOLEAN     DEFAULT TRUE,
    eff_from       TIMESTAMP   DEFAULT now(),
    eff_to         TIMESTAMP
);

CREATE INDEX idx_dim_address_usuario ON dw.dim_address(usuario_id);

CREATE TABLE dw.dim_payment_method (
    payment_method_sk  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    payment_method_id  TEXT,
    name               TEXT,
    description        TEXT
);

CREATE TABLE dw.dim_order_status (
    order_status_sk BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    status_code     TEXT,
    description     TEXT
);

CREATE TABLE dw.dim_review (
    review_sk       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    review_id       TEXT,
    product_sk      BIGINT,
    customer_sk     BIGINT,
    rating          NUMERIC(2,1),
    comment_length  INTEGER,
    review_date     DATE
);

CREATE INDEX idx_dim_review_product ON dw.dim_review(product_sk);
CREATE INDEX idx_dim_review_customer ON dw.dim_review(customer_sk);

CREATE TABLE dw.fact_order (
    order_sk        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id        TEXT        NOT NULL,
    customer_sk     BIGINT,
    date_sk         INTEGER,
    address_sk      BIGINT,
    total_amount    NUMERIC(18,2),
    n_items         INTEGER,
    order_status_sk BIGINT,
    created_at      TIMESTAMP,
    updated_at      TIMESTAMP
);

CREATE INDEX idx_fact_order_customer_sk ON dw.fact_order(customer_sk);
CREATE INDEX idx_fact_order_date_sk ON dw.fact_order(date_sk);
CREATE INDEX idx_fact_order_order_status_sk ON dw.fact_order(order_status_sk);

CREATE TABLE dw.fact_order_line (
    order_line_sk   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id        TEXT        NOT NULL,
    order_sk        BIGINT,
    product_sk      BIGINT,
    customer_sk     BIGINT,
    address_sk      BIGINT,
    date_sk         INTEGER,
    quantity        INTEGER     DEFAULT 1,
    price_unit      NUMERIC(18,2) NOT NULL,
    total           NUMERIC(18,2) GENERATED ALWAYS AS (quantity * price_unit) STORED,
    created_at      TIMESTAMP,
    updated_at      TIMESTAMP
);

CREATE INDEX idx_fact_order_line_product_sk ON dw.fact_order_line(product_sk);
CREATE INDEX idx_fact_order_line_date_sk ON dw.fact_order_line(date_sk);
CREATE INDEX idx_fact_order_line_order_sk ON dw.fact_order_line(order_sk);

CREATE TABLE dw.fact_payment (
    payment_sk      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    payment_id      TEXT,
    order_id        TEXT,
    order_sk        BIGINT,
    payment_method_sk BIGINT,
    date_sk         INTEGER,
    amount          NUMERIC(18,2),
    state_code      TEXT,
    created_at      TIMESTAMP
);

CREATE INDEX idx_fact_payment_order_sk ON dw.fact_payment(order_sk);
CREATE INDEX idx_fact_payment_method_sk ON dw.fact_payment(payment_method_sk);
CREATE INDEX idx_fact_payment_date_sk ON dw.fact_payment(date_sk);

CREATE TABLE dw.fact_inventory_snapshot (
    inventory_sk    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_sk      BIGINT NOT NULL,
    date_sk         INTEGER NOT NULL,
    stock           INTEGER,
    stock_reserved  INTEGER,
    avg_cost        NUMERIC(18,2),
    created_at      TIMESTAMP DEFAULT now()
);

CREATE UNIQUE INDEX ux_inventory_product_date ON dw.fact_inventory_snapshot(product_sk, date_sk);
CREATE INDEX idx_inventory_product_sk ON dw.fact_inventory_snapshot(product_sk);
CREATE INDEX idx_inventory_date_sk ON dw.fact_inventory_snapshot(date_sk);

CREATE TABLE dw.fact_order_accum (
    order_sk        BIGINT PRIMARY KEY,
    order_id        TEXT,
    date_order      DATE,
    order_status_sk BIGINT
);

CREATE INDEX idx_order_accum_status ON dw.fact_order_accum(order_status_sk);

CREATE TABLE dw.fact_ventas_agg_daily (
    agg_id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    date_sk         INTEGER NOT NULL,
    product_sk      BIGINT,
    category_sk     BIGINT,
    cantidad_total  INTEGER,
    ingreso_total   NUMERIC(18,2),
    numero_ordenes  INTEGER
);

CREATE UNIQUE INDEX ux_agg_daily_date_product_category ON dw.fact_ventas_agg_daily(date_sk, product_sk, category_sk);
CREATE INDEX idx_agg_daily_date ON dw.fact_ventas_agg_daily(date_sk);

CREATE INDEX IF NOT EXISTS idx_fact_order_total_amount ON dw.fact_order(total_amount);
CREATE INDEX IF NOT EXISTS idx_fact_order_line_price_unit ON dw.fact_order_line(price_unit);
CREATE INDEX IF NOT EXISTS idx_fact_payment_amount ON dw.fact_payment(amount);
