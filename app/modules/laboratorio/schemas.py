"""DTO de salida de la consulta al laboratorio."""

from pydantic import BaseModel


class StockRead(BaseModel):
    vacuna: str
    stock: int
