from sqlalchemy.orm import Session

from app.models.solicitudes_arco import SolicitudArco
from app.schemas.solicitudes_arco import SolicitudArcoEntrada


def crear_solicitud(db: Session, datos: SolicitudArcoEntrada) -> SolicitudArco:
    solicitud = SolicitudArco(
        nombre=datos.nombre,
        correo=datos.correo,
        tipo_solicitud=datos.tipo_solicitud,
        mensaje=datos.mensaje,
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)
    return solicitud
