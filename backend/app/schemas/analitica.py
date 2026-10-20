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


# --- Panel general del administrador (distinto del Dashboard de arriba:
# ese es para agencias/entidades -Objetivo 4-, este es operativo interno:
# salud del catálogo, crecimiento de la plataforma, solicitudes ARCO). ---


class TendenciaAdministracion(BaseModel):
    etiquetas: list[str]
    usuarios_nuevos: list[int]
    itinerarios_nuevos: list[int]


class CategoriaConteo(BaseModel):
    categoria: str
    cantidad: int


class LugarValorado(BaseModel):
    nombre: str
    valoracion_promedio: float
    total_valoraciones: int


class PanelAdminMetricas(BaseModel):
    total_usuarios: int
    total_lugares_activos: int
    total_lugares_inactivos: int
    total_itinerarios: int
    valoracion_promedio_general: float | None
    solicitudes_arco_pendientes: int
    tendencia_semanal: TendenciaAdministracion
    lugares_por_categoria: list[CategoriaConteo]
    lugares_mejor_valorados: list[LugarValorado]
