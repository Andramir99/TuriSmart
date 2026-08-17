from sqlalchemy.orm import Session

from app.models.preferencias import Preferencia
from app.models.usuarios import Usuario
from app.schemas.preferencias import PreferenciaEntrada
from app.services import categorias_service


def guardar_preferencias(db: Session, usuario: Usuario, datos: PreferenciaEntrada) -> Preferencia:
    """Crea la fila de preferencias del usuario si no existe, o la
    actualiza si ya existe (preferencias es 1 a 1 con usuarios). Así, si
    el usuario vuelve a usar el wizard, sus preferencias quedan al día en
    vez de acumular filas viejas.
    """
    preferencia = usuario.preferencia
    if preferencia is None:
        preferencia = Preferencia(usuario_id=usuario.id)
        db.add(preferencia)

    preferencia.presupuesto = datos.presupuesto
    preferencia.tipo_viaje = datos.tipo_viaje
    preferencia.tiempo_disponible_dias = datos.tiempo_disponible_dias
    preferencia.distrito_partida = datos.distrito_partida
    preferencia.distancia_maxima_km = datos.distancia_maxima_km
    preferencia.categorias = categorias_service.obtener_por_slugs(db, datos.categorias)

    db.commit()
    db.refresh(preferencia)
    return preferencia
