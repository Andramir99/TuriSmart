"""POST /interacciones. Igual que /valoraciones: funciona con o sin
sesión iniciada.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencias import obtener_usuario_opcional
from app.database.conexion import get_db
from app.models.usuarios import Usuario
from app.schemas.interacciones import InteraccionEntrada, InteraccionPublica
from app.services import interacciones_service

router = APIRouter(prefix="/interacciones", tags=["Interacciones"])


@router.post("", response_model=InteraccionPublica, status_code=status.HTTP_201_CREATED)
def crear_interaccion(
    datos: InteraccionEntrada,
    usuario: Usuario | None = Depends(obtener_usuario_opcional),
    db: Session = Depends(get_db),
):
    usuario_id = usuario.id if usuario else None
    return interacciones_service.crear_interaccion(db, usuario_id, datos)
