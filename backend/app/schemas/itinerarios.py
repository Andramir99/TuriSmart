from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.lugares import LugarPublico


class ParadaEntrada(BaseModel):
    lugar_id: int
    dia_numero: int = Field(ge=1)
    hora_inicio: time | None = None
    duracion_min: int | None = Field(default=None, ge=1)
    nota: str | None = Field(default=None, max_length=255)


class ItinerarioEntrada(BaseModel):
    titulo: str = Field(min_length=3, max_length=150)
    fecha_inicio: date | None = None
    presupuesto: str = Field(pattern="^(economico|moderado|premium)$")
    tipo_grupo: str = Field(pattern="^(solo|pareja|familia|amigos)$")
    numero_personas: int = Field(default=1, ge=1, le=20)
    recomendacion_ia: str | None = None
    # "dias" no se pide: se calcula solo como el día más alto entre las
    # paradas (evita que alguien mande dias=5 con paradas solo en el día 1).
    paradas: list[ParadaEntrada] = Field(min_length=1)


class ParadaPublica(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dia_numero: int
    orden: int
    hora_inicio: time | None
    duracion_min: int | None
    nota: str | None
    visitado: bool
    lugar: LugarPublico


class ParadaActualizarEntrada(BaseModel):
    visitado: bool


class ItinerarioRenombrarEntrada(BaseModel):
    titulo: str = Field(min_length=3, max_length=150)


class ReordenarParadasEntrada(BaseModel):
    dia_numero: int = Field(ge=1)
    # ids de DetalleItinerario en el nuevo orden deseado para ese día.
    orden_ids: list[int] = Field(min_length=1)


class ItinerarioPublico(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    fecha_inicio: date | None
    dias: int
    presupuesto: str
    tipo_grupo: str
    numero_personas: int
    presupuesto_estimado_min: float | None
    presupuesto_estimado_max: float | None
    presupuesto_por_dia: dict[int, float]
    distancia_estimada_km: float | None
    recomendacion_ia: str | None
    generado_por_ia: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    detalles: list[ParadaPublica]


class ItinerarioResumen(BaseModel):
    id: int
    titulo: str
    fecha_inicio: date | None
    dias: int
    presupuesto: str
    tipo_grupo: str
    total_lugares: int
    fecha_creacion: datetime
