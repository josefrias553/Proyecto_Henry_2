import csv
import logging
from sqlalchemy import exc
from datetime import datetime
from db import SessionLocal
from models import ResenaProducto, Usuario, Producto
from utils import map_row_keys, exists_by_unique, get_csv_path

CSV_PATH = get_csv_path("resenas_productos.csv")

def load_resenas_productos(csv_path=CSV_PATH):
    with SessionLocal() as session:
        created = 0

        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for raw in reader:
                row = map_row_keys(raw)

                usuario_id = row.get("usuarioid")
                producto_id = row.get("productoid")

                if not usuario_id or not producto_id:
                    continue

                if not session.get(Usuario, int(usuario_id)):
                    continue

                if not session.get(Producto, int(producto_id)):
                    continue

                fecha_raw = row.get("fecha")
                fecha = None
                if fecha_raw:
                    try:
                        fecha = datetime.strptime(fecha_raw, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        pass

                calificacion_raw = row.get("calificacion")
                try:
                    calificacion = int(calificacion_raw) if calificacion_raw else 0
                except Exception:
                    calificacion = 0

                comentario = row.get("comentario") or None

                if exists_by_unique(session, ResenaProducto,
                                    usuario_id=int(usuario_id),
                                    producto_id=int(producto_id),
                                    comentario=comentario,
                                    fecha=fecha):
                    continue

                res = ResenaProducto(
                    usuario_id=int(usuario_id),
                    producto_id=int(producto_id),
                    calificacion=calificacion,
                    comentario=comentario,
                    fecha=fecha
                )

                session.add(res)
                created += 1

        try:
            session.commit()
        except exc.SQLAlchemyError:
            session.rollback()
            raise

        logging.info(f"[Reseñas] Inserciones: {created}")