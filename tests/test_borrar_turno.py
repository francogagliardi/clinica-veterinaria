"""DELETE /turnos/{id} — caso C-05 y RN-09.

Al borrar un turno, sus prácticas las borra la base con ON DELETE CASCADE. El
catálogo de prácticas y los demás turnos no cambian.
"""

from __future__ import annotations

import asyncio

from test_ejercicio4_turnos import _contar, _cuerpo, _entorno

from app.modules.practicas.models import Practica
from app.modules.turnos.models import Turno, TurnoPractica


def test_borrar_turno_borra_sus_practicas_y_deja_el_resto():
    asyncio.run(_caso_borrar_turno())


async def _caso_borrar_turno():
    async with _entorno() as (cliente, sesion, ids):
        cuerpo = _cuerpo(ids["mascota"], ids["p1"], ids["p2"])
        a_borrar = (await cliente.post("/turnos/", json=cuerpo)).json()["id"]
        otro = (await cliente.post("/turnos/", json=cuerpo)).json()["id"]

        respuesta = await cliente.delete(f"/turnos/{a_borrar}")

        assert respuesta.status_code == 204, respuesta.text
        assert respuesta.content == b""
        assert (await cliente.get(f"/turnos/{a_borrar}")).status_code == 404
        assert await _contar(sesion, Turno) == 1
        # Quedan sólo las dos prácticas del otro turno, que sigue completo.
        assert await _contar(sesion, TurnoPractica) == 2
        assert len((await cliente.get(f"/turnos/{otro}")).json()["practicas"]) == 2
        assert await _contar(sesion, Practica) == 2


def test_borrar_turno_inexistente_responde_404():
    asyncio.run(_caso_borrar_inexistente())


async def _caso_borrar_inexistente():
    async with _entorno() as (cliente, sesion, ids):
        turno = (await cliente.post("/turnos/", json=_cuerpo(ids["mascota"], ids["p1"]))).json()["id"]

        respuesta = await cliente.delete("/turnos/9999")

        assert respuesta.status_code == 404
        assert (await cliente.get(f"/turnos/{turno}")).status_code == 200
