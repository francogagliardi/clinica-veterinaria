"""Rutas HTTP del catalogo de practicas."""

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.practicas import service
from app.modules.practicas.schemas import PracticaCreate, PracticaRead

router = APIRouter(prefix="/practicas", tags=["practicas"])


@router.post("/", response_model=PracticaRead, status_code=status.HTTP_201_CREATED)
async def crear_practica(datos: PracticaCreate, session: AsyncSession = Depends(get_session)):
    return await service.crear(session, datos)


@router.get("/", response_model=list[PracticaRead])
async def listar_practicas(session: AsyncSession = Depends(get_session)):
    return await service.listar(session)
