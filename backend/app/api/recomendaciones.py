"""POST /recomendaciones — recomendador por reglas (Etapa 9), funciona
con o sin sesión iniciada.

POST /recomendaciones/ml — recomendador de Machine Learning (Etapa 14-15),
EXIGE sesión iniciada y al menos una valoración de 4-5 estrellas: arma el
perfil del usuario a partir de su propio historial, no de lo que declaró
en un formulario.

GET /recomendaciones/ml/estado — info pública del modelo activo (nombre,
versión, métricas, fecha de entrenamiento), para que el frontend pueda
mostrar "recomendado por IA entrenada el <fecha>" o esconder esa opción
si todavía no hay ningún modelo activo.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencias import obtener_usuario_actual, obtener_usuario_opcional
from app.database.conexion import get_db
from app.models.usuarios import Usuario
from app.schemas.recomendaciones import ModeloActivoPublico, RecomendacionEntrada, RecomendacionPublica
from app.services import recomendaciones_hibrido_service, recomendaciones_ml_service, recomendaciones_service

router = APIRouter(prefix="/recomendaciones", tags=["Recomendaciones"])


@router.post("", response_model=list[RecomendacionPublica])
def generar_recomendaciones(
    datos: RecomendacionEntrada,
    usuario: Usuario | None = Depends(obtener_usuario_opcional),
    db: Session = Depends(get_db),
):
    usuario_id = usuario.id if usuario else None
    return recomendaciones_service.generar_recomendaciones(db, usuario_id, datos)


@router.get("/ml/estado", response_model=ModeloActivoPublico | None)
def ver_estado_modelo_ml(db: Session = Depends(get_db)):
    return recomendaciones_ml_service.obtener_info_modelo_activo(db)


@router.post("/ml", response_model=list[RecomendacionPublica])
def generar_recomendaciones_ml(
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    try:
        return recomendaciones_ml_service.generar_recomendaciones_ml(db, usuario.id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))


@router.get("/para-ti", response_model=list[RecomendacionPublica])
def recomendaciones_para_ti(
    cantidad: int = 10,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    """Sección "Recomendados para ti": combina el perfil dinámico (lo que
    el usuario buscó, filtró, revisó, calificó o agregó a su itinerario)
    con el KNN offline y la popularidad, con una porción de descubrimiento
    para no mostrar siempre la misma categoría.
    """
    return recomendaciones_hibrido_service.generar_recomendaciones_para_ti(db, usuario.id, cantidad=cantidad)
