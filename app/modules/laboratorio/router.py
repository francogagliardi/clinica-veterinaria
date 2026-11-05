"""Rutas HTTP del laboratorio: reciben, delegan en el service y declaran la respuesta."""

from fastapi import APIRouter

from app.modules.laboratorio import service
from app.modules.laboratorio.schemas import StockRead

router = APIRouter(prefix="/laboratorio", tags=["laboratorio"])


@router.get("/stock/{vacuna}", response_model=StockRead)
async def consultar_stock(vacuna: str):
    return await service.obtener_stock(vacuna)
