import csv
import logging
from sqlalchemy import exc
from datetime import datetime
from decimal import Decimal
from db import SessionLocal
from models import HistorialPago, Orden, MetodoPago
from utils import map_row_keys, exists_by_unique, get_csv_path

CSV_PATH = get_csv_path("historial_pagos.csv")

def load_historial_pagos(csv_path=CSV_PATH):
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

                if not session.query(Orden).filter_by(orden_id=int(orden_id)).first():
                    continue
                if not session.query(MetodoPago).filter_by(metodo_pago_id=int(metodo_id)).first():
                    continue

                if exists_by_unique(session, HistorialPago, orden_id=int(orden_id), metodo_pago_id=int(metodo_id)):
                    continue

                monto_raw = row.get("monto")
                try:
                    monto = Decimal(monto_raw) if monto_raw else Decimal(0)
                except Exception:
                    monto = Decimal(0)

                fecha_raw = row.get("fechadepago") or row.get("fechapago")
                fecha_pago = None
                if fecha_raw:
                    try:
                        fecha_pago = datetime.strptime(fecha_raw, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        pass

                pago = HistorialPago(
                    orden_id=int(orden_id),
                    metodo_pago_id=int(metodo_id),
                    monto=monto,
                    fecha_pago=fecha_pago,
                    estado_pago=row.get("estadopago") or "Procesando"
                )

                session.add(pago)
                created += 1

        try:
            session.commit()
        except exc.SQLAlchemyError:
            session.rollback()
            raise

        logging.info(f"[HistorialPagos] Inserciones: {created}")