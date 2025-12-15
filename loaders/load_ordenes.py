import csv
import logging
from sqlalchemy import exc
from datetime import datetime
from decimal import Decimal
from db import SessionLocal
from models import Orden, Usuario
from utils import map_row_keys, exists_by_unique, get_csv_path

CSV_PATH = get_csv_path("ordenes.csv")

def load_ordenes(csv_path=CSV_PATH):
    with SessionLocal() as session:
        created = 0

        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for raw in reader:
                row = map_row_keys(raw)

                usuario_id = row.get("usuarioid")
                if not usuario_id:
                    continue

                if not session.query(Usuario).filter_by(usuario_id=int(usuario_id)).first():
                    continue

                fecha_raw = row.get("fechaorden")
                fecha_orden = None
                if fecha_raw:
                    try:
                        fecha_orden = datetime.strptime(fecha_raw, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        pass

                total_raw = row.get("total")
                try:
                    total = Decimal(total_raw) if total_raw else Decimal(0)
                except Exception:
                    total = Decimal(0)

                if exists_by_unique(session, Orden, usuario_id=int(usuario_id), fecha_orden=fecha_orden, total=total):
                    continue

                orden = Orden(
                    usuario_id=int(usuario_id),
                    fecha_orden=fecha_orden,
                    total=total,
                    estado=row.get("estado") or "Pendiente"
                )

                session.add(orden)
                created += 1

        try:
            session.commit()
        except exc.SQLAlchemyError:
            session.rollback()
            raise

        logging.info(f"[Ordenes] Inserciones: {created}")