"""Tabla "perfiles": datos personales del turista (1 a 1 con usuarios).

Se separó de "usuarios" para que la tabla de login (usuarios) quede
mínima y estable, y todo lo editable desde "Mi perfil" viva aparte.
"""

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Perfil(Base):
    __tablename__ = "perfiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), unique=True, nullable=False)

    pais_origen: Mapped[str | None] = mapped_column(String(80))
    telefono: Mapped[str | None] = mapped_column(String(30))
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date)
    idioma_preferido: Mapped[str] = mapped_column(String(10), nullable=False, default="es")
    movilidad_reducida: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    foto_url: Mapped[str | None] = mapped_column(String(500))

    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="perfil")
