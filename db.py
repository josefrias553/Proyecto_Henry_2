from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from models import Base

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

def create_tables():
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS public"))
        conn.commit()
    Base.metadata.create_all(engine)