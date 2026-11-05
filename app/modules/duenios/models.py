"""Tablas `duenio` y `ficha_duenio`.

Ojo: este archivo NO usa `from __future__ import annotations`; SQLModel necesita
leer los tipos reales de las relaciones.
"""

from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.mascotas.models import Mascota


class Duenio(SQLModel, table=True):
    __tablename__ = "duenio"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    email: str = Field(unique=True)  # RN-01

    # Uno a uno: devuelve UN objeto (o None), no una lista.
    # "all": la ficha la borra la base con ON DELETE CASCADE; el ORM no la toca.
    ficha: Optional["FichaDuenio"] = Relationship(back_populates="duenio", passive_deletes="all")
    # Agregación: un dueño tiene muchas mascotas.
    # "all": el ORM no pone duenio_id en NULL al borrar; decide el RESTRICT (RN-08).
    mascotas: list["Mascota"] = Relationship(back_populates="duenio", passive_deletes="all")


class FichaDuenio(SQLModel, table=True):
    __tablename__ = "ficha_duenio"

    id: int | None = Field(default=None, primary_key=True)
    # La clave foránea va en la ficha (la que depende del dueño). UNIQUE => RN-03.
    # CASCADE: una ficha no tiene sentido sin su dueño.
    duenio_id: int = Field(foreign_key="duenio.id", unique=True, ondelete="CASCADE")
    telefono: str
    direccion: str

    duenio: Duenio = Relationship(back_populates="ficha")
