"""Configuración común de las pruebas.

Las pruebas no tocan PostgreSQL: usan SQLite en memoria con las mismas tablas,
restricciones y claves foráneas, para poder correr sin Docker.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

# `app.core.config` exige DATABASE_URL al importarse. No se abre ninguna conexión:
# el motor real sólo se crea en el lifespan de la app.
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://prueba:prueba@localhost:5433/prueba"
)
