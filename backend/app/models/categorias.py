"""Tabla "categorias": Cultura, Naturaleza, Gastronomía, Aventura, Relax,
Nocturno... Es la versión en base de datos de src/data/tiposViajeroMock.js
y src/utils/categorias.js del frontend (Etapa 3): cada lugar pertenece a
una, y un usuario puede marcar varias como interés (preferencia_categoria).
"""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    nombre: Mapped[str] = mapped_column(String(80), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(255))
    icono: Mapped[str | None] = mapped_column(String(60))
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    lugares: Mapped[list["Lugar"]] = relationship(back_populates="categoria")
