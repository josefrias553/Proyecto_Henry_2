# 🏗️ Proyecto Data Warehouse E-Commerce (M2)

## Visión General
Este proyecto representa una solución de Data Warehouse robusta y escalable diseñada para una plataforma de E-Commerce de alto volumen. Implementa un pipeline ELT (Extract, Load, Transform) completo utilizando **Python** para la ingesta de datos y **dbt (data build tool)** para el modelado dimensional y las transformaciones. La arquitectura sigue las mejores prácticas en Ingeniería de Datos, enfocándose en la modularidad, la calidad de los datos y la reproducibilidad.

## 📐 Arquitectura
El sistema está diseñado con una arquitectura en capas:

1.  **Capa de Ingesta (EL)**: Los loaders basados en Python extraen datos de fuentes crudas (CSV/JSON/API) y los cargan en el Operational Data Store (ODS) de **PostgreSQL**. Esto asegura que se mantenga estrictamente una copia cruda de los datos.
2.  **Capa de Transformación (T)**: `dbt` gestiona el ciclo de vida de la transformación, promoviendo los datos a través de tres capas clave:
    *   **Staging**: Vista 1:1 de las tablas fuente con conversión de tipos, renombrado y limpieza ligera.
    *   **Intermediate**: Joins lógicos, limpieza compleja y aplicación de lógica de negocio.
    *   **Mart**: Modelos dimensionales finales (Esquema Estrella) optimizados para herramientas de BI y análisis OLAP (tablas `dim_*` y `fact_*`).

## 🗄️ Arquitectura de Base de Datos

El proyecto utiliza **PostgreSQL** con una arquitectura de **dos esquemas** para separar las operaciones transaccionales (OLTP) de las analíticas (OLAP):

### **Esquema `public` - OLTP (Operational Database)**
**Propósito**: Base de datos operacional que soporta las transacciones del e-commerce en tiempo real.

**Tablas**:
- `usuarios` - Información de clientes registrados
- `productos` - Catálogo de productos
- `categorias` - Categorías de productos
- `ordenes` - Órdenes de compra
- `detalleordenes` - Líneas de pedido (ítems por orden)
- `direccionesenvio` - Direcciones de envío de usuarios
- `metodospago` - Métodos de pago disponibles
- `ordenesmetodospago` - Relación orden-método de pago
- `historialpagos` - Historial de transacciones de pago
- `resenasproductos` - Reseñas y calificaciones de productos
- `carrito` - Carrito de compras activo

**Características**:
- Normalizado (3NF) para evitar redundancia
- Optimizado para operaciones CRUD (Create, Read, Update, Delete)
- Alta frecuencia de escrituras y actualizaciones
- Cargado por Python loaders desde archivos CSV/JSON

### **Esquema `dw` - OLAP (Data Warehouse)**
**Propósito**: Data Warehouse optimizado para análisis, reportería y business intelligence.

**Dimensiones** (Tablas `dim_*`):
- `dim_time` - Calendario con atributos fiscales y temporales
- `dim_customer` - Clientes con historial (SCD2)
- `dim_customer_segment` - Segmentación de clientes
- `dim_product` - Productos con historial de cambios (SCD2)
- `dim_category` - Categorías de productos
- `dim_address` - Direcciones con historial (SCD2)
- `dim_payment_method` - Métodos de pago
- `dim_order_status` - Estados de órdenes
- `dim_review` - Reseñas de productos

**Hechos** (Tablas `fact_*`):
- `fact_order` - Órdenes (nivel orden)
- `fact_order_line` - Líneas de pedido (nivel ítem)
- `fact_payment` - Pagos y transacciones
- `fact_inventory_snapshot` - Snapshots diarios de inventario
- `fact_order_accum` - Ciclo de vida de órdenes (accumulating snapshot)
- `fact_ventas_agg_daily` - Agregados diarios de ventas

**Características**:
- Desnormalizado (Star Schema) para consultas rápidas
- Historial completo con SCD2 en dimensiones críticas
- Generado y mantenido por transformaciones dbt
- Optimizado para agregaciones y análisis multidimensional

### **Flujo de Datos**
```
Fuentes Raw (CSV/JSON)
        ↓
[Python Loaders] → Esquema 'public' (ODS)
        ↓
[dbt - Staging] → Limpieza y normalización
        ↓
[dbt - Intermediate] → Lógica de negocio
        ↓
[dbt - Mart] → Esquema 'dw' (Star Schema)
        ↓
Herramientas BI (PowerBI, Tableau, Metabase)
```

## 🛠️ Tech Stack
*   **Orquestación y Scripting**: Python 3.8+
*   **Data Warehouse / Base de Datos**: PostgreSQL
*   **Transformación**: dbt Core
*   **Calidad y Testing**: dbt Tests, Python `unittest`

## 🚀 Guía de Inicio

### Requisitos Previos
*   Python 3.8 o superior
*   Instancia de PostgreSQL en ejecución y accesible
*   Conocimiento básico de SQL y herramientas CLI

### Instalación

1.  **Clonar el repositorio**:
    ```bash
    git clone <url-del-repositorio>
    cd Proyecto_Henry_2_V1
    ```

2.  **Configurar el entorno**:
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Unix/MacOS
    source .venv/bin/activate
    ```

3.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuración**:
    *   Copiar `.env.example` a `.env`.
    *   Actualizar `.env` con tus credenciales de PostgreSQL.
    *   Asegurar que tu `profiles.yml` para dbt esté configurado correctamente (apuntado por `dbt_project.yml`).

## ⚙️ Uso

El proyecto utiliza un punto de entrada CLI unificado `main.py` para todas las tareas de ingesta.

### Ingesta de Datos (Loaders)
Inicializar el esquema de la base de datos y cargar todos los datasets:
```bash
python main.py --init-db --load all
```

Cargar una entidad específica (ej., solo usuarios):
```bash
python main.py --load usuarios
```

### Transformaciones dbt

Ejecutar todos los modelos dbt (staging → intermediate → mart):
```bash
dbt run
```

Ejecutar solo una capa específica:
```bash
# Solo staging
dbt run --select staging

# Solo intermediate
dbt run --select intermediate

# Solo mart (dimensiones y hechos)
dbt run --select mart
```

Ejecutar un modelo específico:
```bash
dbt run --select dim_customer
dbt run --select fact_order_line
```

Ejecutar pruebas de calidad de datos:
```bash
dbt test
```

Generar documentación:
```bash
dbt docs generate
dbt docs serve
```

### Validación para GitHub

Antes de subir el proyecto a GitHub, verificar que los archivos sensibles estén excluidos:
```bash
# Verificar estado de git
git status

# Los siguientes archivos NO deben aparecer:
# - .env (credenciales)
# - __pycache__/ (cache de Python)
# - .venv/ (entorno virtual)
# - target/ (artifacts de dbt)
# - dbt_packages/ (paquetes descargados)
# - logs/ y *.log (archivos de log)
```

## 📂 Estructura del Proyecto

```
├── analysis/               # Scripts de análisis ad-hoc y chequeos de calidad
├── data/                   # Almacenamiento de datos crudos
├── dbt_ecommerce_dw/       # Modelos dbt
│   └── models/             # Lógica SQL para Staging, Intermediate y Marts
├── dbt_project.yml         # Configuración de dbt
├── loaders/                # Scripts Python para ingesta de datos (Extract/Load)
├── docs/                   # Activos de documentación
├── SQL/                    # Scripts SQL auxiliares
├── tests/                  # Tests unitarios Python y Tests singulares dbt
├── main.py                 # Punto de entrada CLI
├── models.py               # Definiciones ORM de SQLAlchemy
├── db.py                   # Gestor de conexión a base de datos
└── utils.py                # Funciones auxiliares
```

## 📊 Estrategia de Modelado de Datos

El Data Warehouse está construido bajo un enfoque de **Esquema Estrella**:

*   **Tablas de Hechos (Fact)**: Capturan procesos de negocio (ej., `fact_orders`, `fact_sales`).
*   **Tablas de Dimensiones (Dimension)**: Proveen contexto (ej., `dim_product`, `dim_customer`, `dim_time`).

Esta estructura asegura un alto rendimiento para consultas analíticas e integración fluida con herramientas de BI como PowerBI, Tableau o Metabase.



