"""Contratos (DTO) de duenios y fichas. No son las tablas: son lo que viaja por HTTP."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class FichaCreate(BaseModel):
    telefono: str = Field(min_length=1)
    direccion: str = Field(min_length=1)


class FichaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    duenio_id: int
    telefono: str
    direccion: str


class DuenioCreate(BaseModel):  # sin id: lo pone la base
    nombre: str = Field(min_length=1)
    email: EmailStr


class DuenioUpdate(BaseModel):
    """PATCH: todos los campos son opcionales; se aplica solo lo que se envia."""

    nombre: str | None = Field(default=None, min_length=1)
    email: EmailStr | None = None

    @model_validator(mode="after")
    def _no_permitir_null_explicito(self) -> "DuenioUpdate":
        # Omitir un campo esta bien; mandarlo en null no (las columnas son NOT NULL).
        for campo in self.model_fields_set:
            if getattr(self, campo) is None:
                raise ValueError(f"'{campo}' no puede ser null")
        return self


class DuenioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: str
    ficha: FichaRead | None = None
