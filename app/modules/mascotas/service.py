"""Logica de mascotas."""

import math

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.mascotas.models import Mascota
from app.modules.mascotas.schemas import MascotaCreate, MascotaPagina


async def crear(session: AsyncSession, datos: MascotaCreate) -> Mascota:
    mascota = Mascota(**datos.model_dump())
    session.add(mascota)
    try:
        await session.commit()
    except IntegrityError:  # la clave foranea rechazo un duenio_id inexistente
        await session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, f"No existe el dueño {datos.duenio_id}")
    return mascota


async def obtener_con_duenio(session: AsyncSession, mascota_id: int) -> Mascota:
    consulta = select(Mascota).where(Mascota.id == mascota_id).options(joinedload(Mascota.duenio))
    mascota = (await session.exec(consulta)).unique().one_or_none()
    if mascota is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No existe la mascota {mascota_id}")
    return mascota


async def listar(session: AsyncSession, page: int, size: int) -> MascotaPagina:
    total = (await session.exec(select(func.count()).select_from(Mascota))).one()
    pages = math.ceil(total / size)
    # La primera pagina siempre responde; las demas deben existir.
    if page > max(pages, 1):
        raise HTTPException(
            422,
            f"La página {page} no existe: hay {pages} página(s)",
        )
    consulta = select(Mascota).order_by(Mascota.id).offset((page - 1) * size).limit(size)
    items = list((await session.exec(consulta)).all())
    return MascotaPagina(items=items, total=total, page=page, size=size, pages=pages)
