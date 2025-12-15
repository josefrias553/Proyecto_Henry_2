import argparse
import logging
import sys
from db import create_tables
from loaders.load_usuarios import load_usuarios
from loaders.load_categorias import load_categorias
from loaders.load_metodos_pago import load_metodos_pago
from loaders.load_productos import load_productos
from loaders.load_direcciones_envio import load_direcciones_envio
from loaders.load_carrito import load_carrito
from loaders.load_ordenes import load_ordenes
from loaders.load_detalle_ordenes import load_detalle_ordenes
from loaders.load_ordenes_metodos_pago import load_ordenes_metodos_pago
from loaders.load_resenas_productos import load_resenas_productos
from loaders.load_historial_pagos import load_historial_pagos


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("execution.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

LOADERS = {
    "usuarios": load_usuarios,
    "categorias": load_categorias,
    "metodos_pago": load_metodos_pago,
    "productos": load_productos,
    "direcciones_envio": load_direcciones_envio,
    "carrito": load_carrito,
    "ordenes": load_ordenes,
    "detalle_ordenes": load_detalle_ordenes,
    "ordenes_metodos_pago": load_ordenes_metodos_pago,
    "resenas_productos": load_resenas_productos,
    "historial_pagos": load_historial_pagos
}

def run_all_loaders():
    logging.info("Iniciando proceso de carga de datos completo...")

    steps = [
        "usuarios", "categorias", "metodos_pago",
        "productos", "direcciones_envio", "carrito",
        "ordenes", "detalle_ordenes", "ordenes_metodos_pago",
        "resenas_productos", "historial_pagos"
    ]
    for step in steps:
        logging.info(f"Ejecutando cargador: {step}")
        try:
            LOADERS[step]()
        except Exception as e:
            logging.error(f"Falla al cargar {step}: {e}")
            raise

def main():
    parser = argparse.ArgumentParser(description="CLI de Carga ETL")
    parser.add_argument("--load", choices=list(LOADERS.keys()) + ["all"], default="all", help="Cargador específico a ejecutar o 'all' para todos")
    parser.add_argument("--init-db", action="store_true", help="Inicializar tablas de la base de datos antes de cargar")
    
    args = parser.parse_args()

    try:
        if args.init_db:
            logging.info("Inicializando tablas de base de datos...")
            create_tables()
            logging.info("Tablas creadas.")

        if args.load == "all":
            run_all_loaders()
        else:
            logging.info(f"Ejecutando cargador específico: {args.load}")
            LOADERS[args.load]()
            
        logging.info("Proceso completado exitosamente.")
        
    except Exception as e:
        logging.critical(f"El proceso falló: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
