"""Contratos (DTO) de turnos.

En el alta viajan ids para la asociación (mascota) y para el catálogo de
prácticas; el precio y el total NO viajan: los pone el servidor (RN-06).
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TurnoPracticaCreate(BaseModel):
    """En la composición viaja sólo el id: la fila nace con el turno."""

    practica_id: int


class TurnoCreate(BaseModel):
    mascota_id: int  # asociación: viaja el id de una mascota que ya existe
    fecha: datetime
    motivo: str = Field(min_length=1)
    # RN-05: al menos una práctica; una lista vacía la rechaza el DTO con 422.
    practicas: list[TurnoPracticaCreate] = Field(min_length=1)

    @field_validator("fecha")
    @classmethod
    def _exigir_zona_horaria(cls, valor: datetime) -> datetime:
        if valor.tzinfo is None or valor.utcoffset() is None:
            raise ValueError("La fecha debe incluir zona horaria")
        return valor


class MascotaResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    especie: str


class TurnoPracticaRead(BaseModel):
    practica_id: int
    nombre: str
    precio_unitario: Decimal


class TurnoRead(BaseModel):
    id: int
    fecha: datetime
    motivo: str
    total: Decimal
    mascota: MascotaResumen
    practicas: list[TurnoPracticaRead]
