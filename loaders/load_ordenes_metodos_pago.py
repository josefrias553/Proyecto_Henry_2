import csv
import logging
from sqlalchemy import exc
from decimal import Decimal
from db import SessionLocal
from models import OrdenMetodoPago, Orden, MetodoPago
from utils import map_row_keys, exists_by_unique, get_csv_path

CSV_PATH = get_csv_path("ordenes_metodospago.csv")

def load_ordenes_metodos_pago(csv_path=CSV_PATH):
    with SessionLocal() as session:
        created = 0

        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for raw in reader:
                row = map_row_keys(raw)

                orden_id = row.get("ordenid")
                metodo_id = row.get("metodopagoid")

                if not orden_id or not metodo_id:
                    continue

                if not session.get(Orden, int(orden_id)):
                    continue
                if not session.get(MetodoPago, int(metodo_id)):
                    continue

                if exists_by_unique(session, OrdenMetodoPago, orden_id=int(orden_id), metodo_pago_id=int(metodo_id)):
                    continue

                monto_raw = row.get("montopagado")
                try:
                    monto_pagado = Decimal(monto_raw) if monto_raw else Decimal(0)
                except Exception:
                    monto_pagado = Decimal(0)

                omp = OrdenMetodoPago(
                    orden_id=int(orden_id),
                    metodo_pago_id=int(metodo_id),
                    monto_pagado=monto_pagado
                )

                session.add(omp)
                created += 1

        try:
            session.commit()
        except exc.SQLAlchemyError:
            session.rollback()
            raise

        logging.info(f"[OrdenMetodoPago] Inserciones: {created}")