"""Tablas "itinerarios" y "detalle_itinerario".

Es el equivalente en base de datos de src/data/itinerariosMock.js
(Etapa 3): un itinerario tiene metadatos generales (título, días,
presupuesto...) y "detalle_itinerario" guarda cada parada (qué lugar, en
qué día, a qué hora, en qué orden).
"""

from datetime import date, datetime, time

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Itinerario(Base):
    __tablename__ = "itinerarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))

    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    fecha_inicio: Mapped[date | None] = mapped_column(Date)
    dias: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    presupuesto: Mapped[str] = mapped_column(String(20), nullable=False, default="moderado")
    tipo_grupo: Mapped[str] = mapped_column(String(20), nullable=False, default="solo")

    presupuesto_estimado_min: Mapped[float | None] = mapped_column(Numeric(8, 2))
    presupuesto_estimado_max: Mapped[float | None] = mapped_column(Numeric(8, 2))
    distancia_estimada_km: Mapped[float | None] = mapped_column(Numeric(6, 2))

    recomendacion_ia: Mapped[str | None] = mapped_column(Text)
    generado_por_ia: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    fecha_creacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="itinerarios")
    detalles: Mapped[list["DetalleItinerario"]] = relationship(
        back_populates="itinerario", cascade="all, delete-orphan", order_by="DetalleItinerario.dia_numero, DetalleItinerario.orden"
    )


class DetalleItinerario(Base):
    __tablename__ = "detalle_itinerario"
    __table_args__ = (
        UniqueConstraint("itinerario_id", "dia_numero", "orden", name="uq_detalle_orden_por_dia"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    itinerario_id: Mapped[int] = mapped_column(ForeignKey("itinerarios.id", ondelete="CASCADE"), nullable=False)
    lugar_id: Mapped[int] = mapped_column(ForeignKey("lugares.id"), nullable=False)

    dia_numero: Mapped[int] = mapped_column(Integer, nullable=False)
    orden: Mapped[int] = mapped_column(Integer, nullable=False)
    hora_inicio: Mapped[time | None] = mapped_column(Time)
    duracion_min: Mapped[int | None] = mapped_column(Integer)
    nota: Mapped[str | None] = mapped_column(String(255))

    itinerario: Mapped["Itinerario"] = relationship(back_populates="detalles")
    lugar: Mapped["Lugar"] = relationship()
