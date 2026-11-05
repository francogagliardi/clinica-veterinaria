"""Consulta a la biblioteca del laboratorio, que no tiene variante asincrónica."""

import asyncio

from app.modules.laboratorio.cliente import consultar_stock
from app.modules.laboratorio.schemas import StockRead


async def obtener_stock(vacuna: str) -> StockRead:
    # La llamada corre en otro hilo: el bucle de eventos sigue atendiendo mientras tanto.
    stock = await asyncio.to_thread(consultar_stock, vacuna)
    return StockRead(vacuna=vacuna, stock=stock)
