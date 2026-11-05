"""Rutas HTTP de mascotas."""

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.mascotas import service
from app.modules.mascotas.schemas import (
    MascotaCreate,
    MascotaDetalleRead,
    MascotaPagina,
    MascotaRead,
)

router = APIRouter(prefix="/mascotas", tags=["mascotas"])


@router.post("/", response_model=MascotaRead, status_code=status.HTTP_201_CREATED)
async def crear_mascota(datos: MascotaCreate, session: AsyncSession = Depends(get_session)):
    return await service.crear(session, datos)


@router.get("/", response_model=MascotaPagina)
async def listar_mascotas(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    return await service.listar(session, page, size)


@router.get("/{mascota_id}", response_model=MascotaDetalleRead)
async def obtener_mascota(mascota_id: int, session: AsyncSession = Depends(get_session)):
    return await service.obtener_con_duenio(session, mascota_id)
