import unicodedata
import bcrypt
from sqlalchemy import select
from pathlib import Path

def normalize_header(h: str) -> str:
    nf = unicodedata.normalize("NFKD", h)
    s = "".join(c for c in nf if not unicodedata.combining(c))
    return s.replace("ñ", "n").replace(" ", "").strip().lower()

def map_row_keys(row):
    return { normalize_header(k): v for k, v in row.items() }

def hash_password(cleartext: str) -> str:
    if not cleartext:
        return ""
    hashed = bcrypt.hashpw(cleartext.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

def exists_by_unique(session, model, **kwargs) -> bool:
    stmt = select(model).filter_by(**kwargs).limit(1)
    return session.execute(stmt).scalar_one_or_none() is not None

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data/raw"

def get_csv_path(filename: str) -> str:
    return str(DATA_DIR / filename)

