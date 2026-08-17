"""Tablas "encuestas" y "respuestas_encuesta".

Una encuesta puede responderse SIN estar registrado (la Home promete
"itinerario personalizado... sin registro previo"), por eso usuario_id es
opcional. "respuestas_encuesta" guarda una fila por cada pregunta
respondida (pregunta/respuesta como texto libre) en vez de una columna
por pregunta, porque el enunciado pide capturar muchos campos distintos
(categorías, presupuesto, tiempo, distrito, distancia máxima, compañía,
horario, lugares visitados, valoraciones, recomendaciones aceptadas o
rechazadas, satisfacción...) y no todas las encuestas futuras preguntarán
exactamente lo mismo. Este diseño flexible evita rehacer la tabla cada
vez que se agregue una pregunta nueva.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Encuesta(Base):
    __tablename__ = "encuestas"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id", ondelete="SET NULL"))

    # Consentimiento explícito para usar las respuestas de forma académica
    # y anonimizada (requisito del enunciado). Sin esto en True, esta
    # encuesta no debería usarse para entrenar el modelo (Etapa 13).
    consentimiento_datos: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    version_encuesta: Mapped[str] = mapped_column(String(10), nullable=False, default="1.0")
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    respuestas: Mapped[list["RespuestaEncuesta"]] = relationship(
        back_populates="encuesta", cascade="all, delete-orphan"
    )


class RespuestaEncuesta(Base):
    __tablename__ = "respuestas_encuesta"

    id: Mapped[int] = mapped_column(primary_key=True)
    encuesta_id: Mapped[int] = mapped_column(ForeignKey("encuestas.id", ondelete="CASCADE"), nullable=False)

    # Ej: pregunta="presupuesto", respuesta="moderado"
    #     pregunta="categorias_interes", respuesta="cultura,gastronomia"
    pregunta: Mapped[str] = mapped_column(String(80), nullable=False)
    respuesta: Mapped[str] = mapped_column(Text, nullable=False)

    encuesta: Mapped["Encuesta"] = relationship(back_populates="respuestas")
