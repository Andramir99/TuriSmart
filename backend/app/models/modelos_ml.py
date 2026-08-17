"""Tabla "modelos_ml": registro/versionado de cada modelo entrenado
(Etapas 14-15). No confundir con la carpeta app/ml/: esa carpeta tendrá
el CÓDIGO Python que entrena y carga modelos; esta tabla guarda el
HISTORIAL de modelos ya entrenados (nombre, versión, métricas, si está
activo en producción).

En la Etapa 9, el recomendador inicial basado en reglas también puede
registrarse aquí (tipo="reglas") para que "recomendaciones.modelo_id"
siempre apunte a algo, sea o no un modelo de Machine Learning todavía.
"""

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ModeloML(Base):
    __tablename__ = "modelos_ml"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)  # reglas | knn | colaborativo | hibrido

    metricas: Mapped[dict | None] = mapped_column(JSON)  # Precision@K, Recall@K, NDCG@K
    ruta_archivo: Mapped[str | None] = mapped_column(String(300))

    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    fecha_entrenamiento: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
