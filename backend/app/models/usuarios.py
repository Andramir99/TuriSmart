"""Tabla "usuarios": cuentas de la plataforma.

La contraseña NUNCA se guarda en texto plano: contrasena_hash guarda el
resultado de un algoritmo de hash (bcrypt, vía passlib), que se implementa
en la Etapa 7 junto con el registro/login. Aquí solo definimos la forma
de la tabla.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    correo: Mapped[str] = mapped_column(String(180), nullable=False, unique=True, index=True)
    contrasena_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(20), nullable=False, default="turista")
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # "uselist=False" porque es una relación 1 a 1 (un usuario tiene, a lo
    # sumo, un perfil y una fila de preferencias).
    perfil: Mapped["Perfil"] = relationship(back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    preferencia: Mapped["Preferencia"] = relationship(back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    itinerarios: Mapped[list["Itinerario"]] = relationship(back_populates="usuario")
