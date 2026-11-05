"""Rutas HTTP de duenios: reciben, delegan en el service y declaran la respuesta."""

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.duenios import service
from app.modules.duenios.schemas import (
    DuenioCreate,
    DuenioRead,
    DuenioUpdate,
    FichaCreate,
    FichaRead,
)
from app.modules.mascotas.schemas import MascotaRead

router = APIRouter(prefix="/duenios", tags=["duenios"])


@router.post("/", response_model=DuenioRead, status_code=status.HTTP_201_CREATED)
async def crear_duenio(datos: DuenioCreate, session: AsyncSession = Depends(get_session)):
    return await service.crear(session, datos)


@router.get("/{duenio_id}", response_model=DuenioRead)
async def obtener_duenio(duenio_id: int, session: AsyncSession = Depends(get_session)):
    return await service.obtener_con_ficha(session, duenio_id)


@router.patch("/{duenio_id}", response_model=DuenioRead)
async def modificar_duenio(
    duenio_id: int, datos: DuenioUpdate, session: AsyncSession = Depends(get_session)
):
    return await service.modificar(session, duenio_id, datos)


@router.delete("/{duenio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def borrar_duenio(duenio_id: int, session: AsyncSession = Depends(get_session)) -> None:
    await service.borrar(session, duenio_id)


@router.post("/{duenio_id}/ficha", response_model=FichaRead, status_code=status.HTTP_201_CREATED)
async def crear_ficha(
    duenio_id: int, datos: FichaCreate, session: AsyncSession = Depends(get_session)
):
    return await service.crear_ficha(session, duenio_id, datos)


@router.get("/{duenio_id}/mascotas", response_model=list[MascotaRead])
async def mascotas_del_duenio(duenio_id: int, session: AsyncSession = Depends(get_session)):
    return await service.listar_mascotas(session, duenio_id)
