import csv
import logging
from sqlalchemy import exc
from db import SessionLocal
from models import DireccionEnvio, Usuario
from utils import map_row_keys, exists_by_unique, get_csv_path

CSV_PATH = get_csv_path("direcciones_envio.csv")

def load_direcciones_envio(csv_path=CSV_PATH):
    with SessionLocal() as session:
        created = 0

        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for raw in reader:
                row = map_row_keys(raw)

                usuario_id = row.get("usuarioid")
                calle = row.get("calle")
                ciudad = row.get("ciudad")
                pais = row.get("pais")

                if not usuario_id or not calle or not ciudad or not pais:
                    continue

                if not session.get(Usuario, int(usuario_id)):
                    continue

                calle = calle.strip()
                ciudad = ciudad.strip()
                pais = pais.strip()

                if exists_by_unique(
                    session,
                    DireccionEnvio,
                    usuario_id=int(usuario_id),
                    calle=calle,
                    ciudad=ciudad,
                    pais=pais
                ):
                    continue

                direccion = DireccionEnvio(
                    usuario_id=int(usuario_id),
                    calle=calle,
                    ciudad=ciudad,
                    departamento=row.get("departamento") or None,
                    provincia=row.get("provincia") or None,
                    distrito=row.get("distrito") or None,
                    estado=row.get("estado") or None,
                    codigo_postal=row.get("codigopostal") or None,
                    pais=pais
                )

                session.add(direccion)
                created += 1

        try:
            session.commit()
        except exc.SQLAlchemyError:
            session.rollback()
            raise

        logging.info(f"[Direcciones] Inserciones: {created}")