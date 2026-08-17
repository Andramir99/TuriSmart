from pydantic import BaseModel, Field

from app.schemas.lugares import LugarPublico


class RecomendacionEntrada(BaseModel):
    categorias: list[str] = Field(default_factory=list)  # slugs, ej: ["cultural", "natural"]
    presupuesto: str = Field(default="moderado", pattern="^(economico|moderado|premium)$")
    distrito_partida: str | None = None
    distancia_maxima_km: float | None = Field(default=None, ge=0, le=200)


class RecomendacionPublica(BaseModel):
    lugar: LugarPublico
    puntuacion: float
    motivo: str
