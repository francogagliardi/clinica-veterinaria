"""Deja la base en un estado conocido: borra las tablas y las crea de nuevo.

Uso:  python reiniciar.py
(Los datos iniciales se agregan en el ejercicio 3.)
"""

import asyncio

from sqlmodel import SQLModel

from app.core.database import crear_engine
from app.modules.duenios import models as _duenios  # noqa: F401  (registra las tablas)
from app.modules.mascotas import models as _mascotas  # noqa: F401
from app.modules.practicas import models as _practicas  # noqa: F401


async def main() -> None:
    engine = crear_engine()
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.run_sync(SQLModel.metadata.create_all)
    finally:
        await engine.dispose()
    print("Base reiniciada: tablas creadas.")


if __name__ == "__main__":
    asyncio.run(main())
