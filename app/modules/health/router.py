"""Rutas de salud del servicio.

- /health/live  : ¿el proceso está vivo? No toca la base.
- /health/ready : ¿puede atender? Necesita que PostgreSQL conteste.
"""

from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])

TIMEOUT_BASE_SEGUNDOS = 2.0


@router.get("/live", summary="El proceso está vivo (no consulta la base)")
async def live() -> dict[str, str]:
    return {"estado": "vivo"}


@router.get(
    "/ready",
    summary="La base de datos responde",
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Base caída o lenta"}},
)
async def ready(session: AsyncSession = Depends(get_session)) -> JSONResponse:
    try:
        # El timeout evita que un host que no contesta deje la petición colgada.
        async with asyncio.timeout(TIMEOUT_BASE_SEGUNDOS):
            await session.execute(text("SELECT 1"))
    except Exception as exc:  # conexión rechazada, timeout, credenciales, etc.
        logger.warning("Health ready falló: %r", exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"estado": "no_listo", "base": "sin_conexion"},
        )
    return JSONResponse(status_code=status.HTTP_200_OK, content={"estado": "listo", "base": "ok"})
