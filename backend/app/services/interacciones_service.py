"""Registrar un evento (vista, clic, recomendación aceptada/rechazada...).

Cuando el evento es "recomendacion_aceptada" o "recomendacion_rechazada"
y sabemos quién es el usuario, además actualizamos la fila correspondiente
en "recomendaciones" (fue_aceptada, que desde la Etapa 9 quedaba siempre
en None/pendiente). Esto solo es posible para usuarios con sesión
iniciada: sin una cuenta, no hay forma de saber cuál de las
recomendaciones anónimas de antes está reaccionando ahora.
"""

from sqlalchemy.orm import Session

from app.models.interacciones import Interaccion
from app.models.recomendaciones import Recomendacion
from app.schemas.interacciones import InteraccionEntrada

TIPOS_DE_RECOMENDACION = {
    "recomendacion_aceptada": True,
    "recomendacion_rechazada": False,
}


def crear_interaccion(db: Session, usuario_id: int | None, datos: InteraccionEntrada) -> Interaccion:
    interaccion = Interaccion(
        usuario_id=usuario_id,
        lugar_id=datos.lugar_id,
        itinerario_id=datos.itinerario_id,
        tipo_interaccion=datos.tipo_interaccion,
        metadatos=datos.metadatos,
    )
    db.add(interaccion)
    db.commit()
    db.refresh(interaccion)

    if usuario_id and datos.lugar_id and datos.tipo_interaccion in TIPOS_DE_RECOMENDACION:
        _actualizar_recomendacion(
            db, usuario_id, datos.lugar_id, TIPOS_DE_RECOMENDACION[datos.tipo_interaccion]
        )

    return interaccion


def _actualizar_recomendacion(db: Session, usuario_id: int, lugar_id: int, aceptada: bool) -> None:
    recomendacion = (
        db.query(Recomendacion)
        .filter(Recomendacion.usuario_id == usuario_id, Recomendacion.lugar_id == lugar_id)
        .order_by(Recomendacion.fecha_generacion.desc())
        .first()
    )
    if recomendacion is not None:
        recomendacion.fue_aceptada = aceptada
        db.commit()
