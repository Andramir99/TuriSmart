"""Tabla "solicitudes_arco": canal real para que cualquier persona ejerza
sus derechos ARCO (Acceso, Rectificación, Cancelación, Oposición) sobre
sus datos personales, según la Ley N.° 29733.

No exige sesión iniciada a propósito: alguien que respondió una encuesta
de forma anónima, o que ya no puede entrar a su cuenta, también tiene
derecho a pedir qué se hizo con su información. "atendida" la marca un
administrador manualmente una vez resuelta la solicitud (el prototipo no
automatiza la ejecución de la solicitud, solo su recepción y registro).
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SolicitudArco(Base):
    __tablename__ = "solicitudes_arco"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    correo: Mapped[str] = mapped_column(String(180), nullable=False, index=True)

    # 'acceso' | 'rectificacion' | 'cancelacion' | 'oposicion'
    tipo_solicitud: Mapped[str] = mapped_column(String(20), nullable=False)
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)

    atendida: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
