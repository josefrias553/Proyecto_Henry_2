from sqlalchemy import (Column, Integer, String, Text, Numeric, ForeignKey, DateTime, CheckConstraint, UniqueConstraint, MetaData)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base(metadata=MetaData(schema="public"))

USUARIO_FK = "usuarios.usuario_id"
PRODUCTO_FK = "productos.producto_id"
ORDEN_FK   = "ordenes.orden_id"

# 🍎 Usuarios
class Usuario(Base):
    __tablename__ = "usuarios"

    usuario_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    dni = Column(String(20), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    contrasena = Column(String(255), nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    ordenes = relationship("Orden", back_populates="usuario")
    direcciones = relationship("DireccionEnvio", back_populates="usuario")
    carrito = relationship("Carrito", back_populates="usuario")
    resenas = relationship("ResenaProducto", back_populates="usuario")


# 🍎 Categorías
class Categoria(Base):
    __tablename__ = "categorias"

    categoria_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255))

    productos = relationship("Producto", back_populates="categoria")


# 🍎 Productos
class Producto(Base):
    __tablename__ = "productos"

    producto_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text)
    precio = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.categoria_id"))

    categoria = relationship("Categoria", back_populates="productos")
    detalle_ordenes = relationship("DetalleOrden", back_populates="producto")
    resenas = relationship("ResenaProducto", back_populates="producto")
    carrito_items = relationship("Carrito", back_populates="producto")


# 🍎 Órdenes
class Orden(Base):
    __tablename__ = "ordenes"

    orden_id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey(USUARIO_FK))
    fecha_orden = Column(DateTime, default=datetime.utcnow)
    total = Column(Numeric(10, 2), nullable=False)
    estado = Column(String(50), default="Pendiente")

    usuario = relationship("Usuario", back_populates="ordenes")
    detalle = relationship("DetalleOrden", back_populates="orden")
    pagos = relationship("HistorialPago", back_populates="orden")
    metodos_pago = relationship("OrdenMetodoPago", back_populates="orden")


# 🍎 Detalle Órdenes
class DetalleOrden(Base):
    __tablename__ = "detalleordenes"

    detalle_id = Column(Integer, primary_key=True, index=True)
    orden_id = Column(Integer, ForeignKey(ORDEN_FK))
    producto_id = Column(Integer, ForeignKey(PRODUCTO_FK))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)

    orden = relationship("Orden", back_populates="detalle")
    producto = relationship("Producto", back_populates="detalle_ordenes")


# 🍎 Direcciones de Envío
class DireccionEnvio(Base):
    __tablename__ = "direccionesenvio"

    direccion_id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey(USUARIO_FK))
    calle = Column(String(255), nullable=False)
    ciudad = Column(String(100), nullable=False)
    departamento = Column(String(100))
    provincia = Column(String(100))
    distrito = Column(String(100))
    estado = Column(String(100))
    codigo_postal = Column(String(20))
    pais = Column(String(100), nullable=False)

    usuario = relationship("Usuario", back_populates="direcciones")


# 🍎 Carrito
class Carrito(Base):
    __tablename__ = "carrito"

    carrito_id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey(USUARIO_FK))
    producto_id = Column(Integer, ForeignKey(PRODUCTO_FK))
    cantidad = Column(Integer, nullable=False)
    fecha_agregado = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="carrito")
    producto = relationship("Producto", back_populates="carrito_items")

    __table_args__ = (
        UniqueConstraint("usuario_id", "producto_id", name="uq_carrito_usuario_producto"),
    )


# 🍎 Métodos de Pago
class MetodoPago(Base):
    __tablename__ = "metodospago"

    metodo_pago_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255))

    ordenes_pago = relationship("OrdenMetodoPago", back_populates="metodo")
    historial = relationship("HistorialPago", back_populates="metodo_pago")


# 🍎 Orden + Método de Pago
class OrdenMetodoPago(Base):
    __tablename__ = "ordenesmetodospago"

    orden_metodo_id = Column(Integer, primary_key=True, index=True)
    orden_id = Column(Integer, ForeignKey(ORDEN_FK))
    metodo_pago_id = Column(Integer, ForeignKey("metodospago.metodo_pago_id"))
    monto_pagado = Column(Numeric(10, 2), nullable=False)

    orden = relationship("Orden", back_populates="metodos_pago")
    metodo = relationship("MetodoPago", back_populates="ordenes_pago")


# 🍎 Reseñas de Productos
class ResenaProducto(Base):
    __tablename__ = "resenasproductos"

    resena_id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey(USUARIO_FK))
    producto_id = Column(Integer, ForeignKey(PRODUCTO_FK))
    calificacion = Column(Integer)
    comentario = Column(Text)
    fecha = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="resenas")
    producto = relationship("Producto", back_populates="resenas")

    __table_args__ = (
        CheckConstraint("calificacion >= 1 AND calificacion <= 5", name="chk_calificacion"),
    )


# 🍎 Historial Pagos
class HistorialPago(Base):
    __tablename__ = "historialpagos"

    pago_id = Column(Integer, primary_key=True, index=True)
    orden_id = Column(Integer, ForeignKey(ORDEN_FK))
    metodo_pago_id = Column(Integer, ForeignKey("metodospago.metodo_pago_id"))
    monto = Column(Numeric(10, 2), nullable=False)
    fecha_pago = Column(DateTime, default=datetime.utcnow)
    estado_pago = Column(String(50), default="Procesando")

    orden = relationship("Orden", back_populates="pagos")
    metodo_pago = relationship("MetodoPago", back_populates="historial")