"""Tablas `turno` y `turno_practica`.

Ojo: este archivo NO usa `from __future__ import annotations`; SQLModel necesita
leer los tipos reales de las relaciones.
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Numeric
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.mascotas.models import Mascota
    from app.modules.practicas.models import Practica


class Turno(SQLModel, table=True):
    __tablename__ = "turno"
    __table_args__ = (CheckConstraint("total >= 0", name="ck_turno_total_no_negativo"),)

    id: int | None = Field(default=None, primary_key=True)
    # Asociación: el turno conoce a su mascota. Índice propio: PostgreSQL no lo crea solo.
    mascota_id: int = Field(foreign_key="mascota.id", index=True)
    fecha: datetime = Field(sa_type=DateTime(timezone=True))
    motivo: str
    total: Decimal = Field(sa_type=Numeric(12, 2))

    mascota: "Mascota" = Relationship(back_populates="turnos")
    # Composición: las filas hijas las borra la base (ON DELETE CASCADE, RN-09).
    # "all": el ORM no las carga, no las vacía ni las borra, estén o no en memoria.
    # Con passive_deletes=True no alcanza: si ya están cargadas, intenta poner
    # turno_id en NULL, y turno_id es parte de la clave primaria.
    practicas: list["TurnoPractica"] = Relationship(
        back_populates="turno",
        passive_deletes="all",
    )


class TurnoPractica(SQLModel, table=True):
    """Clase intermedia: guarda el precio cobrado en ESE turno, congelado (RN-06)."""

    __tablename__ = "turno_practica"
    __table_args__ = (
        CheckConstraint("precio_unitario > 0", name="ck_turno_practica_precio_positivo"),
    )

    # Clave primaria compuesta: una práctica no se repite en un turno (RN-07).
    # turno_id no lleva índice propio: es la primera columna de la clave primaria.
    turno_id: int = Field(foreign_key="turno.id", primary_key=True, ondelete="CASCADE")
    # practica_id es la segunda columna de esa clave, por eso sí necesita su índice.
    practica_id: int = Field(foreign_key="practica.id", primary_key=True, index=True)
    # Dinero siempre con Decimal, nunca float.
    precio_unitario: Decimal = Field(sa_type=Numeric(10, 2))

    turno: Turno = Relationship(back_populates="practicas")
    practica: "Practica" = Relationship(back_populates="turnos")
