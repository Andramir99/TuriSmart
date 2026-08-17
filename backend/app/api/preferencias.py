"""POST /preferencias — crea o actualiza las preferencias del usuario
autenticado (presupuesto, tiempo disponible, distrito de partida,
tipo de viaje, distancia máxima, categorías de interés).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencias import obtener_usuario_actual
from app.database.conexion import get_db
from app.models.usuarios import Usuario
from app.schemas.preferencias import PreferenciaEntrada, PreferenciaPublica
from app.services import preferencias_service

router = APIRouter(prefix="/preferencias", tags=["Preferencias"])


@router.post("", response_model=PreferenciaPublica)
def guardar_mis_preferencias(
    datos: PreferenciaEntrada,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    return preferencias_service.guardar_preferencias(db, usuario, datos)
