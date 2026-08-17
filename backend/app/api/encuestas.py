"""POST /encuestas — guarda una respuesta del wizard "Planifica tu viaje".

Funciona con o sin sesión iniciada (obtener_usuario_opcional): si hay un
token válido, la encuesta queda asociada a esa cuenta; si no, se guarda
como anónima. En ambos casos se exige "consentimiento_datos" en True
(validado en el esquema, ver app/schemas/encuestas.py).
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencias import obtener_usuario_opcional
from app.database.conexion import get_db
from app.models.usuarios import Usuario
from app.schemas.encuestas import EncuestaEntrada, EncuestaPublica
from app.services import encuestas_service

router = APIRouter(prefix="/encuestas", tags=["Encuestas"])


@router.post("", response_model=EncuestaPublica, status_code=status.HTTP_201_CREATED)
def registrar_encuesta(
    datos: EncuestaEntrada,
    usuario: Usuario | None = Depends(obtener_usuario_opcional),
    db: Session = Depends(get_db),
):
    usuario_id = usuario.id if usuario else None
    return encuestas_service.crear_encuesta(db, usuario_id, datos)
