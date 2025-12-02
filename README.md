📘 Proyecto M2_V1 — Data Warehouse para E-Commerce

Este proyecto implementa un Data Warehouse completo para un sistema de E-Commerce, empleando Python, PostgreSQL, dbt, y un pipeline de carga y transformación totalmente modularizado.

El objetivo es diseñar un entorno analítico, reproducible y escalable, con buenas prácticas de ingeniería de datos, modelado dimensional y control de calidad.

🧱 Estructura General del Proyecto
M2_V1/
├── .venv/                      # Entorno virtual de Python
├── dbt_packages/               # Paquetes externos utilizados por dbt
├── logs/
│   └── dbt.log                 # Log de ejecuciones de dbt
├── analysis/                   
│   ├── eda_sqlalchemy.py       # Análisis exploratorio vía SQLAlchemy
│   └── quality_checks.py       # Validaciones de calidad de datos
├── data/
│   └── raw/                    # Datos crudos provenientes del OLTP
│   dbt_ecommerce_dw/           # Proyecto dbt (detallado más abajo)
├── docs/                       
│   ├── Modelo Dimensional para E-Commerce
│   ├── Documentación y Justificación del Diseño
│   └── Análisis Exploratorio y Evaluación de Calidad
├── img/                        # Recursos gráficos para documentación
├── loaders/                    # Scripts ETL para poblar el OLTP
│   ├── load_usuarios.py
│   ├── load_productos.py
│   ├── load_ordenes.py
│   ├── load_detalle_ordenes.py
│   ├── load_carrito.py
│   ├── load_direcciones_envio.py
│   ├── load_metodos_pago.py
│   ├── load_historial_pagos.py
│   ├── load_ordenes_metodos_pago.py
│   ├── load_resenas_productos.py
│   └── load_categorias.py
├── notebooks/
│   └── notebook_analysis.ipynb # Análisis exploratorio en Jupyter
├── SQL/
│   └── SQL.sql                 # Script SQL complementario
├── .env                        # Variables de entorno (credenciales/conexión)
├── config.py                   # Configuración general
├── db.py                       # Conexión a la base de datos
├── main.py                     # Ejecución principal del pipeline
├── models.py                   # Modelos de datos en Python
├── utils.py                    # Funciones utilitarias
├── README.md                   # Este archivo
├── dbt_project.yml             # Configuración del proyecto dbt
└── package-lock.yml            # Dependencias del entorno

🏗️ Proyecto dbt: dbt_ecommerce_dw

El corazón del modelado dimensional está en:

data/dbt_ecommerce_dw/

📂 Estructura del proyecto dbt
1. Staging (models/staging/)

Lectura directa de las tablas OLTP (public.*)

Estandarización de nombres, tipos y claves

Preparación de datos crudos para capas posteriores

2. Intermediate (models/intermediate/)

Limpieza avanzada

joins lógicos

normalización y derivación de atributos clave

manejo de duplicados y cálculos previos de métricas

3. Mart (models/mart/)

Incluye:

Dimensiones (mart/dimensions/)

dim_customer

dim_product

dim_category

dim_time

dim_payment_method

dim_location

entre otras

Tablas de hechos (mart/facts/)

fact_order

fact_payment

fact_inventory_snapshot

fact_cart_activity

más métricas agregadas para análisis OLAP

4. Documentación y Tests

schema.yml con:

pruebas de unique, not null, relationships, accepted values

documentación de cada modelo y columna

directorio target/ con modelos compilados y artefactos de ejecución

🔄 Flujo de Trabajo del Pipeline
1. Carga OLTP

Los scripts en loaders/ poblan las tablas transaccionales (public.*) desde archivos externos o fuentes crudas.

2. Transformación dbt

Se ejecuta:

staging → intermediate → mart


Generando un Data Warehouse limpio, documentado y testeado.

3. Análisis

Disponible en:

notebooks/notebook_analysis.ipynb

scripts en analysis/

Incluyen EDA, chequeos de calidad, métricas y validaciones.

