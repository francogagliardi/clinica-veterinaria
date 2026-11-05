"""Rutas HTTP de turnos: reciben, delegan en el service y declaran la respuesta."""

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.turnos import service
from app.modules.turnos.schemas import TurnoCreate, TurnoRead

router = APIRouter(prefix="/turnos", tags=["turnos"])


@router.post("/", response_model=TurnoRead, status_code=status.HTTP_201_CREATED)
async def crear_turno(datos: TurnoCreate, session: AsyncSession = Depends(get_session)):
    return await service.crear(session, datos)


@router.get("/{turno_id}", response_model=TurnoRead)
async def obtener_turno(turno_id: int, session: AsyncSession = Depends(get_session)):
    return await service.obtener(session, turno_id)


@router.delete("/{turno_id}", status_code=status.HTTP_204_NO_CONTENT)
async def borrar_turno(turno_id: int, session: AsyncSession = Depends(get_session)) -> None:
    await service.borrar(session, turno_id)

