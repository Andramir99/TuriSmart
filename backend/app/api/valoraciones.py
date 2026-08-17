"""POST /valoraciones. Funciona con o sin sesión iniciada, igual que
/encuestas y /recomendaciones: valorar no debería exigir cuenta, aunque
si hay una, la valoración queda asociada a ella.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencias import obtener_usuario_opcional
from app.database.conexion import get_db
from app.models.usuarios import Usuario
from app.schemas.valoraciones import ValoracionEntrada, ValoracionPublica
from app.services import valoraciones_service

router = APIRouter(prefix="/valoraciones", tags=["Valoraciones"])


@router.post("", response_model=ValoracionPublica, status_code=status.HTTP_201_CREATED)
def crear_valoracion(
    datos: ValoracionEntrada,
    usuario: Usuario | None = Depends(obtener_usuario_opcional),
    db: Session = Depends(get_db),
):
    usuario_id = usuario.id if usuario else None
    return valoraciones_service.crear_valoracion(db, usuario_id, datos)
