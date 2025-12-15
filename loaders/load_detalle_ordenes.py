import csv
import logging
from sqlalchemy import exc
from decimal import Decimal
from db import SessionLocal
from models import DetalleOrden, Orden, Producto
from utils import map_row_keys, exists_by_unique, get_csv_path

CSV_PATH = get_csv_path("detalle_ordenes.csv")

def load_detalle_ordenes(csv_path=CSV_PATH):
    with SessionLocal() as session:
        created = 0

        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for raw in reader:
                row = map_row_keys(raw)

                orden_id = row.get("ordenid")
                producto_id = row.get("productoid")

                if not orden_id or not producto_id:
                    continue

                if not session.query(Orden).filter_by(orden_id=int(orden_id)).first():
                    continue
                if not session.query(Producto).filter_by(producto_id=int(producto_id)).first():
                    continue

                if exists_by_unique(session, DetalleOrden, orden_id=int(orden_id), producto_id=int(producto_id)):
                    continue

                try:
                    cantidad_val = int(row.get("cantidad") or 1)
                except (TypeError, ValueError):
                    cantidad_val = 1

                precio_raw = row.get("preciounitario")
                try:
                    precio_unitario = Decimal(precio_raw) if precio_raw else Decimal(0)
                except Exception:
                    precio_unitario = Decimal(0)

                detalle = DetalleOrden(
                    orden_id=int(orden_id),
                    producto_id=int(producto_id),
                    cantidad=cantidad_val,
                    precio_unitario=precio_unitario
                )

                session.add(detalle)
                created += 1

        try:
            session.commit()
        except exc.SQLAlchemyError:
            session.rollback()
            raise

        logging.info(f"[DetalleOrdenes] Inserciones: {created}")