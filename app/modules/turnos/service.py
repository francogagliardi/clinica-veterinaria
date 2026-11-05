"""Lógica de turnos.

El alta es una sola transacción: o queda el turno con TODAS sus prácticas, o no
queda nada. El precio se copia del catálogo y el total lo calcula el servidor.
"""

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.practicas.models import Practica
from app.modules.turnos.models import Turno, TurnoPractica
from app.modules.turnos.schemas import (
    MascotaResumen,
    TurnoCreate,
    TurnoPracticaRead,
    TurnoRead,
)


async def crear(session: AsyncSession, datos: TurnoCreate) -> TurnoRead:
    ids = [item.practica_id for item in datos.practicas]

    # Una sola consulta al catálogo: hace falta el precio para copiarlo (RN-06).
    consulta = select(Practica).where(Practica.id.in_(ids))
    catalogo = {practica.id: practica for practica in (await session.exec(consulta)).all()}
    faltantes = [practica_id for practica_id in ids if practica_id not in catalogo]
    if faltantes:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"No existe la práctica {faltantes[0]}: no se guardó nada",
        )

    reservadas = [catalogo[practica_id] for practica_id in ids]
    total = sum((practica.precio for practica in reservadas), start=Decimal("0.00"))

    turno = Turno(
        mascota_id=datos.mascota_id,
        fecha=datos.fecha,
        motivo=datos.motivo,
        total=total,
        # Composición: las filas nacen con el turno y llevan el precio congelado.
        practicas=[
            TurnoPractica(practica_id=practica.id, precio_unitario=practica.precio)
            for practica in reservadas
        ],
    )
    session.add(turno)
    try:
        # Una sola transacción: turno + turno_practica, o nada.
        await session.commit()
    except IntegrityError:
        # Cubre la mascota inexistente y la práctica repetida (clave primaria
        # compuesta, RN-07). Se escribe y decide la base: no hay consulta previa.
        await session.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "No se pudo crear el turno: la mascota no existe o la práctica está repetida",
        )

    return _a_read(await obtener_con_detalle(session, turno.id))


async def obtener_con_detalle(session: AsyncSession, turno_id: int) -> Turno:
    """Turno + mascota (joinedload) + prácticas con su nombre (selectinload): 2 consultas fijas."""
    consulta = (
        select(Turno)
        .where(Turno.id == turno_id)
        .options(
            joinedload(Turno.mascota),
            selectinload(Turno.practicas).joinedload(TurnoPractica.practica),
        )
        .execution_options(populate_existing=True)
    )
    turno = (await session.exec(consulta)).unique().one_or_none()
    if turno is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No existe el turno {turno_id}")
    return turno


async def obtener(session: AsyncSession, turno_id: int) -> TurnoRead:
    """Detalle de un turno para GET /turnos/{id}."""
    return _a_read(await obtener_con_detalle(session, turno_id))


async def borrar(session: AsyncSession, turno_id: int) -> None:
    """Borra el turno; sus prácticas las borra la base con ON DELETE CASCADE (RN-09)."""
    turno = await session.get(Turno, turno_id)
    if turno is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No existe el turno {turno_id}")
    await session.delete(turno)
    await session.commit()


def _a_read(turno: Turno) -> TurnoRead:
    """Arma la respuesta: la práctica aporta su nombre; el precio es el del turno."""
    return TurnoRead(
        id=turno.id,
        fecha=turno.fecha,
        motivo=turno.motivo,
        total=turno.total,
        mascota=MascotaResumen.model_validate(turno.mascota),
        practicas=[
            TurnoPracticaRead(
                practica_id=reservada.practica_id,
                nombre=reservada.practica.nombre,
                precio_unitario=reservada.precio_unitario,
            )
            for reservada in sorted(turno.practicas, key=lambda fila: fila.practica_id)
        ],
    )
