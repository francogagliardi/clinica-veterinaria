"""Motor asincrónico, fábrica de sesiones y dependencia `get_session`.

El motor NO se crea a nivel de módulo: se crea en el lifespan y se guarda en
`app.state`. Por eso `get_session` lo pide prestado a la aplicación que está
atendiendo la petición (`request.app`), en vez de usar una variable global.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings


def crear_engine() -> AsyncEngine:
    """Crea el motor (el pool de conexiones) apuntando a PostgreSQL."""
    return create_async_engine(
        settings.database_url,
        echo=settings.db_echo,  # imprime el SQL: sirve para contar consultas (C-07)
        pool_pre_ping=True,     # descarta conexiones muertas antes de usarlas
    )


def crear_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Devuelve la fábrica: cada llamada produce una sesión nueva."""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,  # los objetos siguen legibles después del commit
    )


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Dependencia: una sesión por petición, abierta y cerrada por FastAPI."""
    session_factory: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    async with session_factory() as session:
        yield session
