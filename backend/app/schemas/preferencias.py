from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.categorias import CategoriaPublica


class PreferenciaEntrada(BaseModel):
    presupuesto: str = Field(pattern="^(economico|moderado|premium)$")
    tipo_viaje: str = Field(pattern="^(solo|pareja|familia|amigos)$")
    tiempo_disponible_dias: int | None = Field(default=None, ge=1, le=30)
    distrito_partida: str | None = Field(default=None, max_length=80)
    distancia_maxima_km: float | None = Field(default=None, ge=0, le=200)
    medio_transporte: str = Field(
        default="cualquiera", pattern="^(a_pie|transporte_publico|auto_taxi|cualquiera)$"
    )
    # Slugs de categorías (ver GET /categorias), ej: ["cultural", "natural"]
    categorias: list[str] = Field(default_factory=list)


class PreferenciaPublica(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    presupuesto: str
    tipo_viaje: str
    tiempo_disponible_dias: int | None
    distrito_partida: str | None
    distancia_maxima_km: float | None
    medio_transporte: str
    fecha_actualizacion: datetime
    categorias: list[CategoriaPublica]
