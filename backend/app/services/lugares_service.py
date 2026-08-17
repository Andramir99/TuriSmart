from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.categorias import Categoria
from app.models.lugares import Lugar


def listar(
    db: Session,
    categoria_slug: str | None = None,
    distrito: str | None = None,
    busqueda: str | None = None,
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

    return consulta.order_by(Lugar.nombre).all()


def obtener_por_id(db: Session, lugar_id: int) -> Lugar | None:
    return (
        db.query(Lugar)
        .options(joinedload(Lugar.categoria))
        .filter(Lugar.id == lugar_id, Lugar.activo.is_(True))
        .first()
    )
