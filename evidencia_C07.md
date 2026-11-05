# Evidencia C-07

## Turno con 1 práctica

```text
2026-11-05 01:43:49,274 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO sqlalchemy.engine.Engine: BEGIN (implicit)
2026-11-05 01:43:49,274 INFO sqlalchemy.engine.Engine SELECT turno.id, turno.mascota_id, turno.fecha, turno.motivo, turno.total, mascota_1.id AS id_1, mascota_1.nombre, mascota_1.especie, mascota_1.duenio_id 
FROM turno LEFT OUTER JOIN mascota AS mascota_1 ON mascota_1.id = turno.mascota_id 
WHERE turno.id = $1::INTEGER
INFO sqlalchemy.engine.Engine: SELECT turno.id, turno.mascota_id, turno.fecha, turno.motivo, turno.total, mascota_1.id AS id_1, mascota_1.nombre, mascota_1.especie, mascota_1.duenio_id 
FROM turno LEFT OUTER JOIN mascota AS mascota_1 ON mascota_1.id = turno.mascota_id 
WHERE turno.id = $1::INTEGER
2026-11-05 01:43:49,274 INFO sqlalchemy.engine.Engine [cached since 0.5646s ago] (2,)
INFO sqlalchemy.engine.Engine: [cached since 0.5646s ago] (2,)
2026-11-05 01:43:49,276 INFO sqlalchemy.engine.Engine SELECT turno_practica.turno_id, turno_practica.practica_id, turno_practica.precio_unitario, practica_1.id, practica_1.nombre, practica_1.precio 
FROM turno_practica LEFT OUTER JOIN practica AS practica_1 ON practica_1.id = turno_practica.practica_id 
WHERE turno_practica.turno_id IN ($1::INTEGER)
INFO sqlalchemy.engine.Engine: SELECT turno_practica.turno_id, turno_practica.practica_id, turno_practica.precio_unitario, practica_1.id, practica_1.nombre, practica_1.precio 
FROM turno_practica LEFT OUTER JOIN practica AS practica_1 ON practica_1.id = turno_practica.practica_id 
WHERE turno_practica.turno_id IN ($1::INTEGER)
2026-11-05 01:43:49,277 INFO sqlalchemy.engine.Engine [cached since 0.5616s ago] (2,)
INFO sqlalchemy.engine.Engine: [cached since 0.5616s ago] (2,)
INFO:     127.0.0.1:63991 - "GET /turnos/2 HTTP/1.1" 200 OK
2026-11-05 01:43:49,279 INFO sqlalchemy.engine.Engine ROLLBACK
INFO sqlalchemy.engine.Engine: ROLLBACK
```

## Turno con 3 prácticas

```text
2026-11-05 01:43:49,809 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO sqlalchemy.engine.Engine: BEGIN (implicit)
2026-11-05 01:43:49,810 INFO sqlalchemy.engine.Engine SELECT turno.id, turno.mascota_id, turno.fecha, turno.motivo, turno.total, mascota_1.id AS id_1, mascota_1.nombre, mascota_1.especie, mascota_1.duenio_id 
FROM turno LEFT OUTER JOIN mascota AS mascota_1 ON mascota_1.id = turno.mascota_id 
WHERE turno.id = $1::INTEGER
INFO sqlalchemy.engine.Engine: SELECT turno.id, turno.mascota_id, turno.fecha, turno.motivo, turno.total, mascota_1.id AS id_1, mascota_1.nombre, mascota_1.especie, mascota_1.duenio_id 
FROM turno LEFT OUTER JOIN mascota AS mascota_1 ON mascota_1.id = turno.mascota_id 
WHERE turno.id = $1::INTEGER
2026-11-05 01:43:49,810 INFO sqlalchemy.engine.Engine [cached since 1.1s ago] (3,)
INFO sqlalchemy.engine.Engine: [cached since 1.1s ago] (3,)
2026-11-05 01:43:49,814 INFO sqlalchemy.engine.Engine SELECT turno_practica.turno_id, turno_practica.practica_id, turno_practica.precio_unitario, practica_1.id, practica_1.nombre, practica_1.precio 
FROM turno_practica LEFT OUTER JOIN practica AS practica_1 ON practica_1.id = turno_practica.practica_id 
WHERE turno_practica.turno_id IN ($1::INTEGER)
INFO sqlalchemy.engine.Engine: SELECT turno_practica.turno_id, turno_practica.practica_id, turno_practica.precio_unitario, practica_1.id, practica_1.nombre, practica_1.precio 
FROM turno_practica LEFT OUTER JOIN practica AS practica_1 ON practica_1.id = turno_practica.practica_id 
WHERE turno_practica.turno_id IN ($1::INTEGER)
2026-11-05 01:43:49,814 INFO sqlalchemy.engine.Engine [cached since 1.1s ago] (3,)
INFO sqlalchemy.engine.Engine: [cached since 1.1s ago] (3,)
INFO:     127.0.0.1:63992 - "GET /turnos/3 HTTP/1.1" 200 OK
2026-11-05 01:43:49,817 INFO sqlalchemy.engine.Engine ROLLBACK
INFO sqlalchemy.engine.Engine: ROLLBACK
```

### Cantidad de consultas SELECT
- **Turno con 1 práctica:** 2 consultas SELECT
- **Turno con 3 prácticas:** 2 consultas SELECT

Ambos bloques coinciden en exactamente 2 consultas SELECT cada uno (2 y 2), demostrando que la carga anticipada resuelve el detalle del turno en un número fijo de consultas que no crece con la cantidad de prácticas (sin caer en el problema N+1).
