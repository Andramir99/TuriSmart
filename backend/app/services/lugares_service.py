from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.categorias import Categoria
from app.models.lugares import Lugar


def listar(
    db: Session,
    categoria_slug: str | None = None,
    distrito: str | None = None,
    busqueda: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    radio_km: float | None = None,
) -> list[Lugar]:
    consulta = (
        db.query(Lugar)
        # joinedload trae la categoría en la MISMA consulta SQL (un JOIN),
        # en vez de una consulta aparte por cada lugar al leer .categoria
        # (el clásico problema "N+1 queries").
        .options(joinedload(Lugar.categoria))
        .filter(Lugar.activo.is_(True))
    )

    if categoria_slug:
        consulta = consulta.join(Categoria).filter(Categoria.slug == categoria_slug)
    if distrito:
        consulta = consulta.filter(Lugar.distrito.ilike(f"%{distrito}%"))
    if busqueda:
        texto = f"%{busqueda}%"
        consulta = consulta.filter(or_(Lugar.nombre.ilike(texto), Lugar.distrito.ilike(texto)))

    if lat is not None and lon is not None:
        # Consulta espacial de verdad, resuelta por PostGIS (no en Python):
        # ST_DWithin filtra por distancia usando el índice GIST de
        # "ubicacion" (Etapa 6), y ST_Distance ordena de más cerca a más
        # lejos. "Cerca de mí" en el Mapa GIS (Etapa 11) usa esto.
        punto_origen = func.ST_GeogFromText(f"POINT({lon} {lat})")
        radio_metros = (radio_km or 5.0) * 1000
        consulta = consulta.filter(func.ST_DWithin(Lugar.ubicacion, punto_origen, radio_metros))
        consulta = consulta.order_by(func.ST_Distance(Lugar.ubicacion, punto_origen))
    else:
        consulta = consulta.order_by(Lugar.nombre)

    return consulta.all()


def obtener_por_id(db: Session, lugar_id: int) -> Lugar | None:
    return (
        db.query(Lugar)
        .options(joinedload(Lugar.categoria))
        .filter(Lugar.id == lugar_id, Lugar.activo.is_(True))
        .first()
    )
