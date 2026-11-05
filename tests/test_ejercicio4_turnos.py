"""Ejercicio 4 — Altas con relaciones: ids y datos.

Se verifica el alta de turnos con sus prácticas en una sola transacción:
- los ids viajan en el DTO (mascota_id, practica_id),
- el precio se copia del catálogo y el total lo calcula el servidor (RN-06),
- al menos una práctica (RN-05) y sin repetidas (RN-07),
- si algo falla no queda guardado ni el turno ni sus prácticas.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from decimal import Decimal

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.duenios.models import Duenio
from app.modules.mascotas.models import Mascota
from app.modules.practicas.models import Practica
from app.modules.turnos.models import Turno, TurnoPractica
from app.modules.turnos.router import router as turnos_router


# ---------------------------------------------------------------------------
# Infraestructura de prueba
# ---------------------------------------------------------------------------


@asynccontextmanager
async def _entorno():
    """Base SQLite en memoria, datos iniciales y cliente HTTP contra el router."""
    motor = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool)

    @event.listens_for(motor.sync_engine, "connect")
    def _activar_claves_foraneas(conexion, _registro):  # pragma: no cover - setup
        conexion.execute("PRAGMA foreign_keys=ON")

    async with motor.begin() as conexion:
        await conexion.run_sync(SQLModel.metadata.create_all)

    fabrica = async_sessionmaker(motor, class_=AsyncSession, expire_on_commit=False)

    async with fabrica() as sesion:
        duenio = Duenio(nombre="Carlos Gómez", email="carlos@example.com")
        consulta = Practica(nombre="Consulta", precio=Decimal("15000.00"))
        vacuna = Practica(nombre="Vacuna antirrábica", precio=Decimal("12000.00"))
        sesion.add_all([duenio, consulta, vacuna])
        await sesion.commit()

        mascota = Mascota(nombre="Toby", especie="perro", duenio_id=duenio.id)
        sesion.add(mascota)
        await sesion.commit()

        ids = {
            "mascota": mascota.id,
            "p1": consulta.id,
            "p2": vacuna.id,
        }

        app = FastAPI()
        app.include_router(turnos_router)

        async def _sesion_de_prueba():
            yield sesion

        app.dependency_overrides[get_session] = _sesion_de_prueba

        transporte = ASGITransport(app=app)
        async with AsyncClient(transport=transporte, base_url="http://prueba") as cliente:
            yield cliente, sesion, ids

    await motor.dispose()


def _cuerpo(mascota_id: int, *practica_ids: int) -> dict:
    return {
        "mascota_id": mascota_id,
        "fecha": "2026-11-12T10:30:00-03:00",
        "motivo": "Control anual",
        "practicas": [{"practica_id": practica_id} for practica_id in practica_ids],
    }


async def _contar(sesion: AsyncSession, modelo) -> int:
    return await sesion.scalar(select(func.count()).select_from(modelo))


# ---------------------------------------------------------------------------
# Casos
# ---------------------------------------------------------------------------


def test_alta_valida_copia_precios_y_calcula_total():
    asyncio.run(_caso_alta_valida())


async def _caso_alta_valida():
    async with _entorno() as (cliente, sesion, ids):
        respuesta = await cliente.post("/turnos/", json=_cuerpo(ids["mascota"], ids["p1"], ids["p2"]))

        assert respuesta.status_code == 201, respuesta.text
        cuerpo = respuesta.json()
        assert Decimal(cuerpo["total"]) == Decimal("27000.00")
        assert cuerpo["mascota"] == {
            "id": ids["mascota"],
            "nombre": "Toby",
            "especie": "perro",
        }
        assert [p["practica_id"] for p in cuerpo["practicas"]] == [ids["p1"], ids["p2"]]
        assert [p["nombre"] for p in cuerpo["practicas"]] == ["Consulta", "Vacuna antirrábica"]
        assert [Decimal(p["precio_unitario"]) for p in cuerpo["practicas"]] == [
            Decimal("15000.00"),
            Decimal("12000.00"),
        ]

        assert await _contar(sesion, Turno) == 1
        assert await _contar(sesion, TurnoPractica) == 2


def test_turno_sin_practicas_responde_422():
    asyncio.run(_caso_sin_practicas())


async def _caso_sin_practicas():
    async with _entorno() as (cliente, sesion, ids):
        cuerpo = _cuerpo(ids["mascota"])
        respuesta = await cliente.post("/turnos/", json=cuerpo)

        assert respuesta.status_code == 422, respuesta.text
        assert await _contar(sesion, Turno) == 0


def test_practica_inexistente_responde_409_y_no_guarda_nada():
    asyncio.run(_caso_practica_inexistente())


async def _caso_practica_inexistente():
    async with _entorno() as (cliente, sesion, ids):
        respuesta = await cliente.post("/turnos/", json=_cuerpo(ids["mascota"], ids["p1"], 9999))

        assert respuesta.status_code == 409, respuesta.text
        assert await _contar(sesion, Turno) == 0
        assert await _contar(sesion, TurnoPractica) == 0


def test_practica_repetida_responde_409_y_no_guarda_nada():
    asyncio.run(_caso_practica_repetida())


async def _caso_practica_repetida():
    async with _entorno() as (cliente, sesion, ids):
        respuesta = await cliente.post("/turnos/", json=_cuerpo(ids["mascota"], ids["p1"], ids["p1"]))

        assert respuesta.status_code == 409, respuesta.text
        assert await _contar(sesion, Turno) == 0
        assert await _contar(sesion, TurnoPractica) == 0


def test_mascota_inexistente_responde_409_y_no_guarda_nada():
    asyncio.run(_caso_mascota_inexistente())


async def _caso_mascota_inexistente():
    async with _entorno() as (cliente, sesion, ids):
        respuesta = await cliente.post("/turnos/", json=_cuerpo(9999, ids["p1"]))

        assert respuesta.status_code == 409, respuesta.text
        assert await _contar(sesion, Turno) == 0
        assert await _contar(sesion, TurnoPractica) == 0


def test_el_precio_cobrado_queda_congelado_en_el_turno():
    asyncio.run(_caso_precio_congelado())


async def _caso_precio_congelado():
    async with _entorno() as (cliente, sesion, ids):
        respuesta = await cliente.post("/turnos/", json=_cuerpo(ids["mascota"], ids["p1"], ids["p2"]))
        assert respuesta.status_code == 201, respuesta.text
        turno_id = respuesta.json()["id"]

        # Cambia el precio del catálogo después de reservar.
        practica = await sesion.get(Practica, ids["p1"])
        practica.precio = Decimal("99999.00")
        sesion.add(practica)
        await sesion.commit()

        filas = (
            await sesion.scalars(
                select(TurnoPractica).where(TurnoPractica.turno_id == turno_id)
            )
        ).all()
        cobrado = {fila.practica_id: fila.precio_unitario for fila in filas}
        assert cobrado[ids["p1"]] == Decimal("15000.00")

        turno = await sesion.get(Turno, turno_id)
        assert turno.total == Decimal("27000.00")
