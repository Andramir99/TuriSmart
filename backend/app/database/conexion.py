"""Conexión a PostgreSQL vía SQLAlchemy.

"engine" es el objeto que sabe hablar con la base de datos (usa la URL de
app/core/config.py). "SessionLocal" crea una "sesión" por cada request:
una especie de conversación temporal con la base de datos para hacer
consultas o guardar cambios. "get_db" es la función que FastAPI usará
(con Depends) para abrir una sesión al empezar un endpoint y cerrarla
automáticamente al terminar, incluso si hubo un error.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# pool_pre_ping revisa que la conexión siga viva antes de usarla; evita
# errores raros si PostgreSQL se reinició y la conexión quedó "colgada".
engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
