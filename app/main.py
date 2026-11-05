"""Aplicación FastAPI: ciclo de vida y registro de routers.

El motor y la fábrica de sesiones nacen en el lifespan y mueren con la app.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import crear_engine, crear_session_factory
from app.modules.duenios.router import router as duenios_router
from app.modules.health.router import router as health_router
from app.modules.mascotas.router import router as mascotas_router
from app.modules.practicas.router import router as practicas_router
from app.modules.turnos.router import router as turnos_router

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("veterinaria")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    engine = crear_engine()
    app.state.engine = engine
    app.state.session_factory = crear_session_factory(engine)
    logger.info("Base de datos: motor creado")
    try:
        yield
    finally:
        await engine.dispose()
        logger.info("Base de datos: motor cerrado")


app = FastAPI(
    title="Veterinaria API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(duenios_router)
app.include_router(mascotas_router)
app.include_router(practicas_router)
app.include_router(turnos_router)
