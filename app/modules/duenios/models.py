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
    ficha: Optional["FichaDuenio"] = Relationship(back_populates="duenio")
    # Agregación: un dueño tiene muchas mascotas.
    mascotas: list["Mascota"] = Relationship(back_populates="duenio")


class FichaDuenio(SQLModel, table=True):
    __tablename__ = "ficha_duenio"

    id: int | None = Field(default=None, primary_key=True)
    # La clave foránea va en la ficha (la que depende del dueño). UNIQUE => RN-03.
    duenio_id: int = Field(foreign_key="duenio.id", unique=True)
    telefono: str
    direccion: str

    duenio: Duenio = Relationship(back_populates="ficha")
