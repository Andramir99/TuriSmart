"""GET /categorias — catálogo de categorías (Cultura, Naturaleza, ...).
Reemplaza a src/data/tiposViajeroMock.js del frontend (Etapa 3): el
wizard "Planifica tu viaje" ahora pide esta lista al backend en vez de
tenerla escrita a mano.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.conexion import get_db
from app.schemas.categorias import CategoriaPublica
from app.services import categorias_service

router = APIRouter(prefix="/categorias", tags=["Categorías"])


@router.get("", response_model=list[CategoriaPublica])
def listar_categorias(db: Session = Depends(get_db)):
    return categorias_service.listar_activas(db)
