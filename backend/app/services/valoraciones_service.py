"""Guardar una valoración (de un lugar o de un itinerario) y, si es de un
lugar, recalcular su promedio en caliente — lugares.valoracion_promedio y
total_valoraciones son columnas "cacheadas" (Etapa 6) para que el
catálogo (Etapa 9) no tenga que promediar en cada consulta.
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.lugares import Lugar
from app.models.valoraciones import Valoracion
from app.schemas.valoraciones import ValoracionEntrada


def crear_valoracion(db: Session, usuario_id: int | None, datos: ValoracionEntrada) -> Valoracion:
    valoracion = Valoracion(
        usuario_id=usuario_id,
        lugar_id=datos.lugar_id,
        itinerario_id=datos.itinerario_id,
        puntuacion=datos.puntuacion,
        recomendacion_util=datos.recomendacion_util,
        estado_visita=datos.estado_visita,
        comentario=datos.comentario,
    )
    db.add(valoracion)
    db.commit()
    db.refresh(valoracion)

    if datos.lugar_id:
        _actualizar_promedio_lugar(db, datos.lugar_id)

    return valoracion


def _actualizar_promedio_lugar(db: Session, lugar_id: int) -> None:
    promedio, total = (
        db.query(func.avg(Valoracion.puntuacion), func.count(Valoracion.id))
        .filter(Valoracion.lugar_id == lugar_id)
        .one()
    )
    lugar = db.query(Lugar).filter(Lugar.id == lugar_id).first()
    if lugar:
        lugar.valoracion_promedio = round(float(promedio or 0), 2)
        lugar.total_valoraciones = total or 0
        db.commit()
