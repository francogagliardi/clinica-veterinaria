"""Tabla `mascota`."""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.duenios.models import Duenio
    from app.modules.turnos.models import Turno


class Mascota(SQLModel, table=True):
    __tablename__ = "mascota"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    especie: str
    # RESTRICT: la base impide borrar un dueño que todavía tiene mascotas (RN-08).
    # Índice propio: PostgreSQL no lo crea solo para las claves foráneas.
    duenio_id: int = Field(foreign_key="duenio.id", ondelete="RESTRICT", index=True)

    duenio: "Duenio" = Relationship(back_populates="mascotas")
    # Asociación: una mascota puede tener muchos turnos.
    turnos: list["Turno"] = Relationship(back_populates="mascota")
