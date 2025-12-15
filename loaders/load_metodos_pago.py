import csv
import logging
from sqlalchemy import exc
from db import SessionLocal
from models import MetodoPago
from utils import map_row_keys, exists_by_unique, get_csv_path

CSV_PATH = get_csv_path("metodos_pago.csv")

def load_metodos_pago(csv_path=CSV_PATH):
    with SessionLocal() as session:
        created = 0
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_raw in reader:
                row = map_row_keys(row_raw)

                nombre = row.get("nombre")
                if not nombre:
                    continue
                nombre = nombre.strip()

                if exists_by_unique(session, MetodoPago, nombre=nombre):
                    continue

                m = MetodoPago(
                    nombre=nombre,
                    descripcion=row.get("descripcion") or None
                )
                session.add(m)
                created += 1

        try:
            session.commit()
        except exc.SQLAlchemyError:
            session.rollback()
            raise

        logging.info(f"[MetodosPago] Inserciones: {created}")