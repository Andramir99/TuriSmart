from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.lugares import LugarPublico


class RecomendacionEntrada(BaseModel):
    categorias: list[str] = Field(default_factory=list)  # slugs, ej: ["cultural", "natural"]
    presupuesto: str = Field(default="moderado", pattern="^(economico|moderado|premium)$")
    distrito_partida: str | None = None
    distancia_maxima_km: float | None = Field(default=None, ge=0, le=200)
    # Cómo prefiere trasladarse el turista entre paradas. Se usa solo para
    # agregar una advertencia honesta en el motivo (ej. "es mucha distancia
    # para ir a pie"), nunca para calcular una ruta real ni un tiempo de
    # traslado — eso requeriría una API de rutas real, fuera de alcance.
    medio_transporte: str = Field(
        default="cualquiera", pattern="^(a_pie|transporte_publico|auto_taxi|cualquiera)$"
    )
    # Declarado por el turista en el wizard (Etapa 8). Se usa para resaltar
    # en el motivo si el lugar está o no señalado como accesible.
    movilidad_reducida: bool = False
    # Cuántas recomendaciones devolver. El wizard (Planificar.jsx) lo
    # calcula según los días del viaje, para que alcancen lugares
    # distintos para cada día en vez de repartir siempre las mismas 5.
    cantidad: int = Field(default=5, ge=1, le=30)


class RecomendacionPublica(BaseModel):
    lugar: LugarPublico
    puntuacion: float
    motivo: str
    # None si no se declaró distrito de partida (no hay con qué comparar).
    distancia_km: float | None = None
    # "cerca" | "moderada" | "lejos" | None — para que el frontend pueda
    # mostrar una etiqueta clara en vez de que la distancia quede oculta
    # dentro del texto del motivo.
    distancia_etiqueta: str | None = None


class ModeloActivoPublico(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    version: str
    tipo: str
    metricas: dict | None
    fecha_entrenamiento: datetime | None
