import csv
import logging
from sqlalchemy import exc
from db import SessionLocal
from models import Usuario
from utils import map_row_keys, hash_password, exists_by_unique, get_csv_path

CSV_PATH = get_csv_path("usuarios.csv")

def load_usuarios(csv_path=CSV_PATH):
    with SessionLocal() as session:
        created = 0
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for raw in reader:
                row = map_row_keys(raw)

                dni = row.get("dni")
                email = row.get("email")

                if not dni or not email:
                    continue

                dni = dni.strip()
                email = email.strip()

                if exists_by_unique(session, Usuario, dni=dni) or exists_by_unique(session, Usuario, email=email):
                    continue

                nombre = row.get("nombre")
                apellido = row.get("apellido")

                user = Usuario(
                    nombre=nombre.strip() if nombre else None,
                    apellido=apellido.strip() if apellido else None,
                    dni=dni,
                    email=email,
                    contrasena=hash_password(
                        (row.get("contrasena") or row.get("contraseña") or "").strip()
                    )
                )
                session.add(user)
                created += 1

        try:
            session.commit()
        except exc.SQLAlchemyError:
            session.rollback()
            raise

        logging.info(f"[Usuarios] Inserciones: {created}")