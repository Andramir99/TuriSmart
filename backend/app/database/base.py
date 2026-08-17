"""Clase base declarativa de SQLAlchemy.

Todos los modelos (app/models/*.py) heredan de esta clase "Base". Alembic
(las migraciones) también la importa para saber qué tablas deberían
existir en la base de datos y generar el SQL de creación automáticamente.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
