"""Contratos (DTO) del catalogo de practicas."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PracticaCreate(BaseModel):
    nombre: str = Field(min_length=1)
    precio: Decimal = Field(gt=0, max_digits=10, decimal_places=2)  # RN-04


class PracticaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    precio: Decimal
