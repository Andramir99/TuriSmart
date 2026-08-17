"""Tabla "preferencias" (1 a 1 con usuarios) + "preferencia_categoria".

preferencia_categoria es una tabla intermedia que no estaba en la lista
mínima del enunciado, pero hace falta: un usuario puede marcar VARIAS
categorías de interés (cultura, gastronomía, ...), y una categoría la
puede elegir mucha gente — es una relación muchos-a-muchos, que en una
base de datos relacional siempre necesita su propia tabla.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Preferencia(Base):
    __tablename__ = "preferencias"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), unique=True, nullable=False)

    presupuesto: Mapped[str] = mapped_column(String(20), nullable=False, default="moderado")
    tiempo_disponible_dias: Mapped[int | None] = mapped_column()
    distrito_partida: Mapped[str | None] = mapped_column(String(80))
    tipo_viaje: Mapped[str] = mapped_column(String(20), nullable=False, default="solo")
    distancia_maxima_km: Mapped[float | None] = mapped_column(Numeric(6, 2))

    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="preferencia")
    categorias: Mapped[list["Categoria"]] = relationship(
        secondary="preferencia_categoria", backref="preferencias"
    )


class PreferenciaCategoria(Base):
    __tablename__ = "preferencia_categoria"

    preferencia_id: Mapped[int] = mapped_column(
        ForeignKey("preferencias.id", ondelete="CASCADE"), primary_key=True
    )
    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.id", ondelete="CASCADE"), primary_key=True
    )
