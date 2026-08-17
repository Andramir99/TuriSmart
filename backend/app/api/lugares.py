"""GET /lugares y GET /lugares/{id} — el catálogo turístico real.
Reemplaza a src/data/destinosMock.js del frontend (Etapa 3).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.conexion import get_db
from app.schemas.lugares import LugarPublico
from app.services import lugares_service

router = APIRouter(prefix="/lugares", tags=["Lugares"])


@router.get("", response_model=list[LugarPublico])
def listar_lugares(
    categoria: str | None = Query(default=None, description="Slug de categoría, ej: cultural"),
    distrito: str | None = Query(default=None),
    q: str | None = Query(default=None, description="Busca en nombre y distrito"),
    db: Session = Depends(get_db),
):
    return lugares_service.listar(db, categoria_slug=categoria, distrito=distrito, busqueda=q)


@router.get("/{lugar_id}", response_model=LugarPublico)
def ver_lugar(lugar_id: int, db: Session = Depends(get_db)):
    lugar = lugares_service.obtener_por_id(db, lugar_id)
    if lugar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lugar no encontrado")
    return lugar
