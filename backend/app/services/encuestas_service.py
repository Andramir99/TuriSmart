from sqlalchemy.orm import Session

from app.models.encuestas import Encuesta, RespuestaEncuesta
from app.schemas.encuestas import EncuestaEntrada


def crear_encuesta(db: Session, usuario_id: int | None, datos: EncuestaEntrada) -> Encuesta:
    encuesta = Encuesta(
        usuario_id=usuario_id,
        consentimiento_datos=datos.consentimiento_datos,
        version_encuesta=datos.version_encuesta,
    )
    db.add(encuesta)
    db.flush()  # asigna encuesta.id sin cerrar la transacción

    for pregunta, respuesta in datos.respuestas.items():
        db.add(RespuestaEncuesta(encuesta_id=encuesta.id, pregunta=pregunta, respuesta=respuesta))

    db.commit()
    db.refresh(encuesta)
    return encuesta
