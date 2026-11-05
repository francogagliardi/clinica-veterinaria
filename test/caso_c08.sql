-- C-08: un precio inválido escrito directo en la base, sin pasar por la API.
-- Se corre después de `python reiniciar.py`:
--   docker exec -i veterinaria-db psql -U postgres -d veterinaria < test/caso_c08.sql
--
-- Esperado: la base lo rechaza por el CHECK y ningún precio cambia.
--   ERROR:  new row for relation "practica" violates check constraint "ck_practica_precio_positivo"

UPDATE practica SET precio = 0;
