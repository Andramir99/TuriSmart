from datetime import date

from pydantic import BaseModel


class EstadisticasGenerales(BaseModel):
    total_itinerarios: int
    promedio_valoracion: float | None
    destino_mas_valorado: str | None
    destino_mas_valorado_total: int
    tasa_aceptacion_recomendaciones: float | None
    total_reacciones_recomendaciones: int


class TendenciaSemanal(BaseModel):
    etiquetas: list[str]
    consultas: list[int]
    itinerarios: list[int]


class DestinoPopular(BaseModel):
    nombre: str
    valor: int


class MetricaTipoGrupo(BaseModel):
    etiqueta: str
    valor: float
    color: str


class ItinerarioReciente(BaseModel):
    id: int
    usuario: str
    color: str
    destinos: str
    dias: int
    satisfaccion: float | None
    fecha: date


class DashboardPublico(BaseModel):
    estadisticas: EstadisticasGenerales
    tendencia_semanal: TendenciaSemanal
    destinos_mas_vistos: list[DestinoPopular]
    metricas_tipo_grupo: list[MetricaTipoGrupo]
    itinerarios_recientes: list[ItinerarioReciente]
    # Honestidad (no ocultar que la plataforma todavía tiene poco uso
    # real): el frontend muestra un aviso si esto es False, en vez de
    # dejar que un panel casi vacío parezca un error.
    datos_suficientes: bool
