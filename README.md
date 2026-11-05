# Veterinaria API

API asincrónica para una veterinaria de barrio: dueños, mascotas, prácticas y turnos.
Trabajo práctico de Programación III (unidades 1 a 4) con FastAPI, SQLModel y
PostgreSQL.

## Requisitos

- Python 3.12 o superior (probado con 3.14).
- Docker con Docker Compose (la base corre en un contenedor).

## Puesta en marcha desde cero

```powershell
# 1. Entorno virtual e dependencias
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# 2. Configuración
Copy-Item env.example .env
#    Editar .env si se quiere otro usuario/clave/puerto.

# 3. Base de datos (PostgreSQL 16 en Docker, publicada en localhost:5433)
docker compose up -d
docker compose ps          # esperar a que diga "healthy"

# 4. Esquema y datos iniciales (a partir del ejercicio 3)
python reiniciar.py

# 5. Servidor
uvicorn app.main:app --reload
```

Documentación interactiva: <http://localhost:8000/docs>

> El contenedor publica el puerto **5433** y no el 5432 para no chocar con un
> PostgreSQL instalado en la máquina. Si se cambia `POSTGRES_PORT`, hay que
> cambiar también el puerto dentro de `DATABASE_URL`.

## Estado del proyecto

- [x] **Ejercicio 1** — estructura, `lifespan`, motor y sesión asíncrona, `/health/live` y `/health/ready`.
- [x] **Ejercicio 2** — DTOs separados, CRUD, PATCH parcial, códigos HTTP y paginación de mascotas.
- [x] **Ejercicio 3** — modelos con restricciones, relaciones navegables, `reiniciar.py` con datos iniciales.
- [ ] **Ejercicio 4** — altas de turnos con prácticas en una sola transacción.
- [ ] **Ejercicio 5** — lecturas con carga anticipada (sin N+1).
- [ ] **Ejercicio 6** — consulta al laboratorio fuera del event loop.

## Variables de entorno

| Variable | Uso |
| --- | --- |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_PORT` | Las usa `compose.yaml` para crear la base. |
| `DATABASE_URL` | Cadena que usa la API. Debe empezar con `postgresql+asyncpg://`. |
| `DB_ECHO` | `true` imprime el SQL en consola (sirve para contar consultas). |

El archivo `.env` no se versiona; `env.example` muestra la forma esperada sin
ningún secreto real.

## Estructura

```
app/
  main.py                 aplicación, lifespan y routers
  core/config.py          lectura y validación de DATABASE_URL
  core/database.py        motor, fábrica de sesiones y get_session
  modules/health/         /health/live y /health/ready
  modules/<módulo>/       models, schemas, service y router
compose.yaml              PostgreSQL 16 para desarrollo
reiniciar.py              borra, crea el esquema y carga datos iniciales
test/                     casos de prueba en archivos .http
```

## Pruebas manuales

Los archivos de `test/` son para la extensión *REST Client* de VS Code y se
ejecutan con el servidor levantado, después de `python reiniciar.py`.

## Por qué `turno_practica.turno_id` no lleva índice propio

La clave primaria `(turno_id, practica_id)` ya crea un índice cuya primera columna es
`turno_id`, y ese índice sirve para buscar por `turno_id` solo. `practica_id` es la
segunda columna: ese índice no sirve para buscar por ella, y por eso lleva uno propio.
