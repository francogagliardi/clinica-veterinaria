"""Tabla `practica` (catálogo de prácticas con su precio)."""

from decimal import Decimal

from sqlalchemy import CheckConstraint, Numeric
from sqlmodel import Field, SQLModel


class Practica(SQLModel, table=True):
    __tablename__ = "practica"
    __table_args__ = (CheckConstraint("precio > 0", name="ck_practica_precio_positivo"),)  # RN-04

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True)  # RN-02
    # Dinero siempre con Decimal, nunca float.
    precio: Decimal = Field(sa_type=Numeric(10, 2))
