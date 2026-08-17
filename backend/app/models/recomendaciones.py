"""Tabla "recomendaciones": cada lugar que el sistema le sugirió a un
usuario, con su puntaje y el motivo explicado (Etapa 9). "modelo_id"
indica qué recomendador la generó — al principio será siempre el mismo
registro de tipo "reglas" en modelos_ml; desde la Etapa 14 puede ser un
modelo de Machine Learning distinto.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Recomendacion(Base):
    __tablename__ = "recomendaciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id", ondelete="SET NULL"))
    lugar_id: Mapped[int] = mapped_column(ForeignKey("lugares.id"), nullable=False)
    encuesta_id: Mapped[int | None] = mapped_column(ForeignKey("encuestas.id", ondelete="SET NULL"))
    modelo_id: Mapped[int | None] = mapped_column(ForeignKey("modelos_ml.id", ondelete="SET NULL"))

    puntuacion: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    motivo: Mapped[str | None] = mapped_column(Text)

    # None = el usuario todavía no reaccionó a esta recomendación.
    fue_aceptada: Mapped[bool | None] = mapped_column(Boolean)

    fecha_generacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
