"""Tabla "valoraciones": lo que el usuario califica después de usar la
plataforma — un lugar puntual o el itinerario completo (por eso lugar_id
e itinerario_id son ambos opcionales: se llena uno u otro, nunca los dos
a la vez; esa regla se valida en el servicio, Etapa 12, no en la base de
datos, para no complicar el modelo con un CHECK constraint prematuro).
"""

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Valoracion(Base):
    __tablename__ = "valoraciones"
    __table_args__ = (
        CheckConstraint("puntuacion BETWEEN 1 AND 5", name="ck_valoracion_puntuacion_1_a_5"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id", ondelete="SET NULL"))
    lugar_id: Mapped[int | None] = mapped_column(ForeignKey("lugares.id", ondelete="SET NULL"))
    itinerario_id: Mapped[int | None] = mapped_column(ForeignKey("itinerarios.id", ondelete="SET NULL"))

    # Solo lectura — igual que en Interaccion, para el perfil dinámico.
    lugar: Mapped["Lugar | None"] = relationship(viewonly=True)

    puntuacion: Mapped[int] = mapped_column(Integer, nullable=False)
    recomendacion_util: Mapped[bool | None] = mapped_column()

    # 'visitado' | 'descartado' | 'pendiente'
    estado_visita: Mapped[str | None] = mapped_column(String(20))
    comentario: Mapped[str | None] = mapped_column(Text)

    # Ver Encuesta.es_sintetico: misma idea, misma Etapa 13.
    es_sintetico: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
