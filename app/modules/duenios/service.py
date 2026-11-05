"""Logica de duenios. Recibe la sesion; traduce los errores de la base a HTTP."""

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.duenios.models import Duenio, FichaDuenio
from app.modules.duenios.schemas import DuenioCreate, DuenioUpdate, FichaCreate
from app.modules.mascotas.models import Mascota


def _no_encontrado(duenio_id: int) -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, f"No existe el dueño {duenio_id}")


async def obtener_con_ficha(session: AsyncSession, duenio_id: int) -> Duenio:
    # joinedload: trae dueño y ficha en UNA consulta (nada de carga perezosa).
    consulta = (
        select(Duenio)
        .where(Duenio.id == duenio_id)
        .options(joinedload(Duenio.ficha))
        .execution_options(populate_existing=True)
    )
    duenio = (await session.exec(consulta)).unique().one_or_none()
    if duenio is None:
        raise _no_encontrado(duenio_id)
    return duenio


async def crear(session: AsyncSession, datos: DuenioCreate) -> Duenio:
    duenio = Duenio(**datos.model_dump())
    session.add(duenio)
    try:
        await session.commit()  # no preguntamos si existe: escribimos y decide la base
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un dueño con ese email")
    return await obtener_con_ficha(session, duenio.id)


async def modificar(session: AsyncSession, duenio_id: int, datos: DuenioUpdate) -> Duenio:
    duenio = await obtener_con_ficha(session, duenio_id)
    duenio.sqlmodel_update(datos.model_dump(exclude_unset=True))  # solo lo enviado
    session.add(duenio)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un dueño con ese email")
    return await obtener_con_ficha(session, duenio_id)


async def borrar(session: AsyncSession, duenio_id: int) -> None:
    duenio = await session.get(Duenio, duenio_id)
    if duenio is None:
        raise _no_encontrado(duenio_id)
    await session.delete(duenio)
    try:
        await session.commit()
    except IntegrityError:  # ON DELETE RESTRICT de mascota.duenio_id
        await session.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, "No se puede borrar: el dueño tiene mascotas a su nombre"
        )


async def crear_ficha(session: AsyncSession, duenio_id: int, datos: FichaCreate) -> FichaDuenio:
    if await session.get(Duenio, duenio_id) is None:
        raise _no_encontrado(duenio_id)
    ficha = FichaDuenio(duenio_id=duenio_id, **datos.model_dump())
    session.add(ficha)
    try:
        await session.commit()
    except IntegrityError:  # UNIQUE en ficha_duenio.duenio_id
        await session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "El dueño ya tiene una ficha")
    return ficha


async def listar_mascotas(session: AsyncSession, duenio_id: int) -> list[Mascota]:
    if await session.get(Duenio, duenio_id) is None:
        raise _no_encontrado(duenio_id)
    consulta = select(Mascota).where(Mascota.duenio_id == duenio_id).order_by(Mascota.id)
    return list((await session.exec(consulta)).all())
