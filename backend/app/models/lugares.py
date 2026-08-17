"""Tabla "lugares": el catálogo turístico. Es el equivalente en base de
datos de src/data/destinosMock.js (Etapa 3): cuando conectemos Explorar,
Mapa GIS y el Dashboard al backend real (Etapa 9), esos mocks se borran y
las pantallas consultan esta tabla.

"ubicacion" usa el tipo Geography de PostGIS (vía GeoAlchemy2) en vez de
dos columnas float (latitud, longitud) sueltas. La ventaja es que
PostGIS puede resolver directamente en la base de datos preguntas como
"¿qué lugares hay a menos de 3 km de aquí?" (ST_DWithin) sin traer todas
las filas a Python para calcular la distancia a mano. El "4326" es el
código EPSG del sistema de coordenadas GPS estándar (el mismo que usan
Leaflet y Google Maps).
"""

from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import ARRAY, Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Lugar(Base):
    __tablename__ = "lugares"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"), nullable=False)

    distrito: Mapped[str] = mapped_column(String(80), nullable=False)
    direccion: Mapped[str | None] = mapped_column(String(255))
    precio: Mapped[float | None] = mapped_column(Numeric(8, 2))
    horario: Mapped[str | None] = mapped_column(String(120))
    duracion_estimada_min: Mapped[int | None] = mapped_column(Integer)

    # Point(longitud, latitud) — en PostGIS y GeoJSON siempre va primero
    # la longitud, al revés de como solemos decir "lat, lon" al hablar.
    ubicacion: Mapped[str] = mapped_column(Geography(geometry_type="POINT", srid=4326), nullable=False)

    accesible_movilidad_reducida: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    imagen_url: Mapped[str | None] = mapped_column(String(500))
    etiquetas: Mapped[list[str] | None] = mapped_column(ARRAY(String(60)))

    valoracion_promedio: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False, default=0)
    total_valoraciones: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    fuente_informacion: Mapped[str | None] = mapped_column(String(120))
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    categoria: Mapped["Categoria"] = relationship(back_populates="lugares")
