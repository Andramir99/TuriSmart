"""GET /analitica/dashboard — Objetivo Específico 4: panel de métricas
para agencias y entidades, calculado en vivo (reemplaza al mock del
frontend, Etapa 3).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencias import obtener_usuario_actual
from app.database.conexion import get_db
from app.models.usuarios import Usuario
from app.schemas.analitica import DashboardPublico
from app.services import analitica_service

router = APIRouter(prefix="/analitica", tags=["Analítica"])

# Por debajo de este umbral de itinerarios reales, el panel se marca como
# "datos_suficientes: false" para que el frontend avise en vez de mostrar
# un panel casi vacío como si fuera un error o un bug.
MINIMO_ITINERARIOS_PARA_PANEL_CONFIABLE = 10


@router.get("/dashboard", response_model=DashboardPublico)
def ver_dashboard(
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    estadisticas = analitica_service.obtener_estadisticas_generales(db)
    return DashboardPublico(
        estadisticas=estadisticas,
        tendencia_semanal=analitica_service.obtener_tendencia_semanal(db),
        destinos_mas_vistos=analitica_service.obtener_destinos_mas_vistos(db),
        metricas_tipo_grupo=analitica_service.obtener_metricas_tipo_grupo(db),
        itinerarios_recientes=analitica_service.obtener_itinerarios_recientes(db),
        datos_suficientes=estadisticas["total_itinerarios"] >= MINIMO_ITINERARIOS_PARA_PANEL_CONFIABLE,
    )
