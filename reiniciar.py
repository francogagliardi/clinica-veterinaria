"""Deja la base en un estado conocido: borra las tablas, las crea y carga los datos.

Uso:  python reiniciar.py
"""

import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import SQLModel

from app.core.database import crear_engine, crear_session_factory
from app.modules.duenios.models import Duenio, FichaDuenio
from app.modules.mascotas.models import Mascota
from app.modules.practicas.models import Practica
from app.modules.turnos.models import Turno, TurnoPractica

ARGENTINA = timezone(timedelta(hours=-3))


async def crear_tablas(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def cargar_datos(engine: AsyncEngine) -> None:
    # Los ids no se escriben a mano: el orden de alta define los que usa test/*.http.
    # Decimal explícito: un modelo con table=True no valida ni convierte lo que recibe.
    consulta = Practica(nombre="Consulta", precio=Decimal("15000.00"))
    desparasitacion = Practica(nombre="Desparasitación", precio=Decimal("8000.00"))
    vacuna = Practica(nombre="Vacuna antirrábica", precio=Decimal("12000.00"))
    analisis = Practica(nombre="Análisis de sangre", precio=Decimal("20000.00"))

    # El dueño 1 queda sin ficha, porque duenios.http le da de alta una (espera 201).
    carlos = Duenio(nombre="Carlos Gómez", email="carlos@example.com")
    laura = Duenio(
        nombre="Laura Díaz",
        email="laura@example.com",
        ficha=FichaDuenio(telefono="11-4444-5678", direccion="Av. Siempre Viva 742"),
    )

    toby = Mascota(nombre="Toby", especie="perro", duenio=carlos)
    michi = Mascota(nombre="Michi", especie="gato", duenio=carlos)
    luna = Mascota(nombre="Luna", especie="perro", duenio=laura)

    session_factory = crear_session_factory(engine)
    async with session_factory() as session:
        # flush antes de crear el turno: los ids del catálogo quedan en este orden. Después,
        # la sesión llegaría primero a las prácticas reservadas siguiendo las relaciones.
        session.add_all([consulta, desparasitacion, vacuna, analisis])
        await session.flush()

        # Igual que en un alta real: el precio se copia del catálogo y el total se calcula.
        reservadas = [consulta, vacuna]
        turno = Turno(
            mascota=toby,
            fecha=datetime(2026, 11, 10, 9, 0, tzinfo=ARGENTINA),
            motivo="Vacunación anual",
            total=sum(practica.precio for practica in reservadas),
            practicas=[
                TurnoPractica(practica=practica, precio_unitario=practica.precio)
                for practica in reservadas
            ],
        )

        session.add_all([carlos, laura, toby, michi, luna, turno])
        await session.commit()  # una sola transacción: o queda todo, o no queda nada


async def main() -> None:
    engine = crear_engine()
    try:
        await crear_tablas(engine)
        await cargar_datos(engine)
    finally:
        await engine.dispose()
    print("Base reiniciada: tablas creadas y datos iniciales cargados.")


if __name__ == "__main__":
    asyncio.run(main())
