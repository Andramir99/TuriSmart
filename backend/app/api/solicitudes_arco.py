"""POST /solicitudes-arco — canal real para ejercer los derechos ARCO
(Acceso, Rectificación, Cancelación, Oposición) sobre datos personales.

No exige sesión iniciada: una encuesta puede haberse respondido de forma
anónima, y aun así la persona tiene derecho a pedir información sobre
cómo se trataron sus datos.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.conexion import get_db
from app.schemas.solicitudes_arco import SolicitudArcoEntrada, SolicitudArcoPublica
from app.services import solicitudes_arco_service

router = APIRouter(prefix="/solicitudes-arco", tags=["Derechos ARCO"])


@router.post("", response_model=SolicitudArcoPublica, status_code=status.HTTP_201_CREATED)
def registrar_solicitud_arco(datos: SolicitudArcoEntrada, db: Session = Depends(get_db)):
    return solicitudes_arco_service.crear_solicitud(db, datos)
