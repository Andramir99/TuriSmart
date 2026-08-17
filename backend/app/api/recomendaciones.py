"""POST /recomendaciones — las 5 mejores sugerencias según el recomendador
inicial basado en reglas (ver app/services/recomendaciones_service.py).
Funciona con o sin sesión iniciada, igual que POST /encuestas.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencias import obtener_usuario_opcional
from app.database.conexion import get_db
from app.models.usuarios import Usuario
from app.schemas.recomendaciones import RecomendacionEntrada, RecomendacionPublica
from app.services import recomendaciones_service

router = APIRouter(prefix="/recomendaciones", tags=["Recomendaciones"])


@router.post("", response_model=list[RecomendacionPublica])
def generar_recomendaciones(
    datos: RecomendacionEntrada,
    usuario: Usuario | None = Depends(obtener_usuario_opcional),
    db: Session = Depends(get_db),
):
    usuario_id = usuario.id if usuario else None
    return recomendaciones_service.generar_recomendaciones(db, usuario_id, datos)
