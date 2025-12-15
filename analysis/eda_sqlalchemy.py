import pandas as pd
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session

from M2.models import (Usuario, Categoria, Producto, Orden, DetalleOrden, DireccionEnvio, Carrito, MetodoPago, OrdenMetodoPago, ResenaProducto, HistorialPago)

def show_columns(model):
    mapper = inspect(model)
    return [(col.key, str(col.type)) for col in mapper.columns]


def count_rows(session: Session, model):
    return session.query(model).count()


def describe_table(session: Session, model):
    return {
        "table": model.__tablename__,
        "columns": show_columns(model),
        "rows": count_rows(session, model),
    }

def table_to_df(session: Session, model):
    query = session.query(model)
    df = pd.read_sql(query.statement, session.bind)
    return df

ALL_TABLES = [Usuario, Categoria, Producto, Orden, DetalleOrden,DireccionEnvio, Carrito, MetodoPago,OrdenMetodoPago, ResenaProducto, HistorialPago]

def run_full_eda(session: Session):
    return [describe_table(session, model) for model in ALL_TABLES]
