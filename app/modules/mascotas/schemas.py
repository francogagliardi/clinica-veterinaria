"""Contratos (DTO) de mascotas y el envoltorio de paginacion."""

from pydantic import BaseModel, ConfigDict, Field


class MascotaCreate(BaseModel):
    nombre: str = Field(min_length=1)
    especie: str = Field(min_length=1)
    duenio_id: int  # agregacion: viaja el id de un dueño que ya existe


class MascotaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    especie: str
    duenio_id: int


class DuenioResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: str


class MascotaDetalleRead(MascotaRead):
    duenio: DuenioResumen


class MascotaPagina(BaseModel):
    items: list[MascotaRead]
    total: int
    page: int
    size: int
    pages: int
