from sqlalchemy.orm import Session

from app.models.categorias import Categoria


def listar_activas(db: Session) -> list[Categoria]:
    return db.query(Categoria).filter(Categoria.activo.is_(True)).order_by(Categoria.id).all()


def obtener_por_slugs(db: Session, slugs: list[str]) -> list[Categoria]:
    if not slugs:
        return []
    return db.query(Categoria).filter(Categoria.slug.in_(slugs)).all()
