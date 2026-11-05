"""Ejercicio 6 — Asincronía sin bloqueos.

La biblioteca del laboratorio es sincrónica y tarda un segundo. Se verifica que:
- GET /laboratorio/stock/{vacuna} informa lo que devuelve esa biblioteca,
- mientras hay consultas en curso, el servidor sigue atendiendo (caso C09),
- todos los handlers de la aplicación son async def.

Estas pruebas no abren ninguna conexión a la base y usan el cliente real, sin
reemplazarlo: si la llamada bloqueara el bucle de eventos, los tiempos lo mostrarían.
"""

from __future__ import annotations

import asyncio
import inspect
import time

import pytest
from fastapi.routing import APIRoute
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.modules.duenios.router import router as duenios_router
from app.modules.health.router import router as health_router
from app.modules.laboratorio.router import router as laboratorio_router
from app.modules.mascotas.router import router as mascotas_router
from app.modules.practicas.router import router as practicas_router
from app.modules.turnos.router import router as turnos_router

ROUTERS = [
    duenios_router,
    health_router,
    laboratorio_router,
    mascotas_router,
    practicas_router,
    turnos_router,
]


def _cliente_http() -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://prueba")


@pytest.mark.parametrize(
    ("vacuna", "stock"),
    [("rabia", 15), ("moquillo", 18)],
)
def test_informa_el_stock_que_devuelve_el_laboratorio(vacuna, stock):
    async def caso():
        async with _cliente_http() as cliente:
            return await cliente.get(f"/laboratorio/stock/{vacuna}")

    respuesta = asyncio.run(caso())

    assert respuesta.status_code == 200
    assert respuesta.json() == {"vacuna": vacuna, "stock": stock}


def test_salud_responde_de_inmediato_durante_tres_consultas_al_laboratorio():
    async def caso():
        async with _cliente_http() as cliente:
            inicio = time.perf_counter()
            consultas = [
                asyncio.create_task(cliente.get(f"/laboratorio/stock/vacuna{i}"))
                for i in range(3)
            ]
            # Le da tiempo a las tres consultas para que estén en curso.
            await asyncio.sleep(0.1)

            inicio_salud = time.perf_counter()
            salud = await cliente.get("/health/live")
            demora_salud = time.perf_counter() - inicio_salud
            consultas_en_curso = sum(not consulta.done() for consulta in consultas)

            respuestas = await asyncio.gather(*consultas)
            demora_total = time.perf_counter() - inicio
        return salud, demora_salud, consultas_en_curso, respuestas, demora_total

    salud, demora_salud, consultas_en_curso, respuestas, demora_total = asyncio.run(caso())

    assert salud.status_code == 200
    assert consultas_en_curso == 3
    assert demora_salud < 0.5
    assert [r.status_code for r in respuestas] == [200, 200, 200]
    # En serie tardarían al menos 3 segundos: corren a la vez, en hilos aparte.
    assert demora_total < 2.5


def test_todos_los_handlers_son_asincronicos():
    # Se miran los routers de cada módulo: las versiones nuevas de FastAPI no exponen
    # sus rutas como APIRoute dentro de app.routes.
    handlers = [
        ruta
        for router in ROUTERS
        for ruta in router.routes
        if isinstance(ruta, APIRoute)
    ]
    sincronicos = [ruta.path for ruta in handlers if not inspect.iscoroutinefunction(ruta.endpoint)]

    assert "/laboratorio/stock/{vacuna}" in [ruta.path for ruta in handlers]
    assert sincronicos == []
