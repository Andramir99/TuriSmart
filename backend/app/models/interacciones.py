"""Tabla "interacciones": bitácora de eventos del usuario dentro de la
plataforma (vio un lugar, le dio clic, lo agregó a un itinerario...).
Junto con "valoraciones", es la materia prima del dataset que se prepara
en la Etapa 13 para entrenar el modelo de recomendación.
"""

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Interaccion(Base):
    __tablename__ = "interacciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id", ondelete="SET NULL"))
    lugar_id: Mapped[int | None] = mapped_column(ForeignKey("lugares.id", ondelete="SET NULL"))
    itinerario_id: Mapped[int | None] = mapped_column(ForeignKey("itinerarios.id", ondelete="SET NULL"))

    # Solo lectura (no back_populates en Lugar: no hace falta navegar en
    # el otro sentido). Se usa para calcular el perfil dinámico por
    # categoría sin tener que hacer una consulta aparte por cada fila.
    lugar: Mapped["Lugar | None"] = relationship(viewonly=True)

    # 'vista' | 'clic' | 'agregado_itinerario' | 'recomendacion_aceptada' | 'recomendacion_rechazada'
    tipo_interaccion: Mapped[str] = mapped_column(String(40), nullable=False)
    metadatos: Mapped[dict | None] = mapped_column(JSON)

    # Ver Encuesta.es_sintetico: misma idea, misma Etapa 13.
    es_sintetico: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
