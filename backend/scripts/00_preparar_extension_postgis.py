"""Habilita la extensión PostGIS si todavía no está activa.

Con Docker Compose local no hace falta: la imagen postgis/postgis ya la
activa sola al crear la base de datos. Pero un PostgreSQL administrado
(como el de Render) la entrega vacía, y las migraciones de Alembic usan
columnas de tipo Geography (geoalchemy2) que requieren PostGIS ya
activo — por eso este paso corre ANTES de "alembic upgrade head" en el
arranque del contenedor (ver Dockerfile).

Primero verifica si ya existe: así, si el rol de conexión no tiene
permiso para crear extensiones (el caso normal en Docker Compose local,
donde PostGIS ya viene activo), el script no intenta nada y no falla.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import text  # noqa: E402

from app.database.conexion import engine  # noqa: E402

with engine.begin() as conexion:
    ya_activa = conexion.execute(
        text("SELECT 1 FROM pg_extension WHERE extname = 'postgis'")
    ).first()

    if ya_activa:
        print("PostGIS ya estaba activo.")
    else:
        conexion.execute(text("CREATE EXTENSION postgis"))
        print("PostGIS activado.")
