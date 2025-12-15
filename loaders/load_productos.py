import csv
import logging
from sqlalchemy import exc
from decimal import Decimal
from db import SessionLocal
from models import Producto, Categoria
from utils import map_row_keys, exists_by_unique, get_csv_path

CSV_PATH = get_csv_path("productos.csv")

def load_productos(csv_path=CSV_PATH):
    with SessionLocal() as session:
        created = 0
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for raw in reader:
                row = map_row_keys(raw)

                nombre = row.get("nombre")
                if not nombre:
                    continue
                nombre = nombre.strip()

                categoria_id_raw = row.get("categoriaid")
                try:
                    categoria_id = int(categoria_id_raw) if categoria_id_raw else None
                except:
                    categoria_id = None

                if exists_by_unique(session, Producto, nombre=nombre, categoria_id=categoria_id):
                    continue

                precio_raw = row.get("precio")
                try:
                    precio = Decimal(precio_raw) if precio_raw else Decimal(0)
                except Exception:
                    precio = Decimal(0)

                stock_raw = row.get("stock")
                try:
                    stock = int(stock_raw) if stock_raw else 0
                except Exception:
                    stock = 0

                prod = Producto(
                    nombre=nombre,
                    descripcion=row.get("descripcion") or None,
                    precio=precio,
                    stock=stock,
                    categoria_id=categoria_id
                )
                session.add(prod)
                created += 1

        try:
            session.commit()
        except exc.SQLAlchemyError:
            session.rollback()
            raise

        logging.info(f"[Productos] Inserciones: {created}")