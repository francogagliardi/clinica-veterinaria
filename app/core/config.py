"""Configuración de la aplicación: se lee del entorno, una sola vez, al arrancar.

`DATABASE_URL` es la única fuente de verdad de la conexión. El archivo `.env`
existe sólo para no tener que exportar variables a mano en cada terminal.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Carga el .env de la raíz del proyecto (no pisa variables ya definidas en el entorno).
load_dotenv()

PREFIJO_ASINCRONICO = "postgresql+asyncpg://"


@dataclass(frozen=True)
class Settings:
    """Configuración ya validada. Si esto existe, la app puede arrancar."""

    database_url: str
    db_echo: bool


def _leer_settings() -> Settings:
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError(
            "Falta la variable DATABASE_URL. Copiá env.example a .env y completala."
        )
    if not url.startswith(PREFIJO_ASINCRONICO):
        raise RuntimeError(
            "DATABASE_URL debe empezar con 'postgresql+asyncpg://'. "
            "Sin '+asyncpg' SQLAlchemy abre una conexión sincrónica y bloquea el servidor."
        )
    return Settings(
        database_url=url,
        db_echo=os.getenv("DB_ECHO", "true").strip().lower() in {"1", "true", "yes", "si"},
    )


settings = _leer_settings()
