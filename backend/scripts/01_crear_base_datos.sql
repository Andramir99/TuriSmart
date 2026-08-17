-- =====================================================================
-- Etapa 5: crea el rol de aplicación y la base de datos de TuriSmart
-- Lima, y habilita la extensión PostGIS.
--
-- Requisito previo: PostGIS ya debe estar instalado sobre tu PostgreSQL
-- (vía Stack Builder). Si "CREATE EXTENSION postgis" falla más abajo,
-- es señal de que ese paso todavía no se hizo.
--
-- Ejecutar UNA sola vez, como superusuario, desde PowerShell:
--   & "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -f 01_crear_base_datos.sql
--
-- Te pedirá la contraseña del superusuario "postgres" (la que elegiste
-- al instalar PostgreSQL), y luego el propio script te pedirá que
-- ELIJAS una contraseña nueva para el rol "turismart_app" (la que usará
-- el backend). Esa contraseña nunca queda escrita en este archivo.
-- =====================================================================

-- 1. Rol de aplicación: el backend NUNCA se conecta como "postgres"
--    (el superusuario), sino con un rol propio y de permisos acotados.
CREATE ROLE turismart_app WITH LOGIN;
\password turismart_app

-- 2. Base de datos, de propiedad de ese rol.
CREATE DATABASE turismart_db OWNER turismart_app;

-- 3. PostGIS se habilita "por base de datos": hay que conectarse a
--    turismart_db (no a "postgres") antes de crear la extensión.
\c turismart_db

CREATE EXTENSION IF NOT EXISTS postgis;

-- 4. Verificación: si esto imprime una versión (por ejemplo "3.4 ..."),
--    PostGIS quedó instalado y habilitado correctamente.
SELECT postgis_full_version();
