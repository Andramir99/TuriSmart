from geoalchemy2.elements import WKTElement
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.categorias import Categoria
from app.models.lugares import Lugar
from app.schemas.lugares import LugarActualizar, LugarCrear

# Para que una búsqueda de texto libre ("museos", "playa cerca") también
# alimente el perfil dinámico (Etapa 16) aunque el usuario no haga clic en
# ningún resultado. Es una heurística simple por palabra clave, no NLP:
# alcanza para el propósito de inferir intención de categoría.
PALABRAS_CLAVE_POR_CATEGORIA: dict[str, list[str]] = {
    "arqueologico": ["huaca", "arqueolog", "piramide", "prehispan"],
    "cultural": ["museo", "histor", "cultura", "arte", "iglesia", "catedral", "convento", "plaza", "colonial"],
    "gastronomico": ["restaurante", "gastronom", "mercado", "comida", "chifa", "pisco", "ceviche"],
    "aventura": ["aventura", "surf", "trekking", "senderismo", "deporte"],
    "natural": ["natural", "parque", "lomas", "bosque", "humedal", "jardin", "playa"],
    "relax": ["relax", "tranquilo", "spa", "malecon"],
    "nocturno": ["bar", "noche", "discoteca", "nocturn"],
}


def inferir_categoria_desde_texto(texto: str) -> str | None:
    texto_normalizado = texto.lower()
    for slug, palabras in PALABRAS_CLAVE_POR_CATEGORIA.items():
        if any(p in texto_normalizado for p in palabras):
            return slug
    return None


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


def crear(db: Session, datos: LugarCrear) -> Lugar:
    lugar = Lugar(
        **datos.model_dump(exclude={"lat", "lon"}),
        ubicacion=WKTElement(f"POINT({datos.lon} {datos.lat})", srid=4326),
    )
    db.add(lugar)
    db.commit()
    db.refresh(lugar)
    return obtener_por_id(db, lugar.id)


def actualizar(db: Session, lugar_id: int, datos: LugarActualizar) -> Lugar | None:
    lugar = obtener_por_id(db, lugar_id)
    if lugar is None:
        return None

    cambios = datos.model_dump(exclude_unset=True, exclude={"lat", "lon"})
    for campo, valor in cambios.items():
        setattr(lugar, campo, valor)

    # lat/lon viajan sueltos en el esquema, pero en la tabla son una sola
    # columna Geography — si llega cualquiera de los dos, hay que
    # recalcular el punto completo (no se puede actualizar solo un eje).
    if datos.lat is not None or datos.lon is not None:
        lugar.ubicacion = WKTElement(
            f"POINT({datos.lon if datos.lon is not None else lugar.lon} "
            f"{datos.lat if datos.lat is not None else lugar.lat})",
            srid=4326,
        )

    db.commit()
    db.refresh(lugar)
    return obtener_por_id(db, lugar.id)


def eliminar(db: Session, lugar_id: int) -> bool:
    """Baja lógica: pone activo=False en vez de borrar la fila, para no
    romper itinerarios, valoraciones e interacciones que ya referencian
    este lugar. listar()/obtener_por_id() ya filtran por activo=True, así
    que deja de aparecer en el catálogo de inmediato.
    """
    lugar = db.query(Lugar).filter(Lugar.id == lugar_id).first()
    if lugar is None:
        return False
    lugar.activo = False
    db.commit()
    return True
