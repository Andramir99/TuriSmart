"""GET /lugares y GET /lugares/{id} — el catálogo turístico real.
Reemplaza a src/data/destinosMock.js del frontend (Etapa 3).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencias import obtener_usuario_opcional
from app.database.conexion import get_db
from app.models.usuarios import Usuario
from app.schemas.interacciones import InteraccionEntrada
from app.schemas.lugares import LugarPublico
from app.services import interacciones_service, lugares_service

router = APIRouter(prefix="/lugares", tags=["Lugares"])


@router.get("", response_model=list[LugarPublico])
def listar_lugares(
    categoria: str | None = Query(default=None, description="Slug de categoría, ej: cultural"),
    distrito: str | None = Query(default=None),
    q: str | None = Query(default=None, description="Busca en nombre y distrito"),
    lat: float | None = Query(default=None, description="Con lon, activa la búsqueda por cercanía (PostGIS)"),
    lon: float | None = Query(default=None),
    radio_km: float | None = Query(default=None, ge=0.1, le=50),
    usuario: Usuario | None = Depends(obtener_usuario_opcional),
    db: Session = Depends(get_db),
):
    resultado = lugares_service.listar(
        db, categoria_slug=categoria, distrito=distrito, busqueda=q, lat=lat, lon=lon, radio_km=radio_km
    )

    # Señal para el perfil dinámico (Etapa 16): solo se registra con sesión
    # iniciada y solo cuando el usuario realmente buscó o filtró algo (no
    # en cada carga del catálogo sin filtros). No bloquea la respuesta si
    # el guardado falla.
    if usuario and (q or categoria or distrito):
        try:
            if q:
                categoria_inferida = lugares_service.inferir_categoria_desde_texto(q)
                interacciones_service.crear_interaccion(
                    db,
                    usuario.id,
                    InteraccionEntrada(
                        tipo_interaccion="busqueda",
                        metadatos={"texto": q, "categoria": categoria_inferida},
                    ),
                )
            if categoria or distrito:
                interacciones_service.crear_interaccion(
                    db,
                    usuario.id,
                    InteraccionEntrada(
                        tipo_interaccion="filtro",
                        metadatos={"categoria": categoria, "distrito": distrito},
                    ),
                )
        except Exception:
            pass

    return resultado


@router.get("/{lugar_id}", response_model=LugarPublico)
def ver_lugar(lugar_id: int, db: Session = Depends(get_db)):
    lugar = lugares_service.obtener_por_id(db, lugar_id)
    if lugar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lugar no encontrado")
    return lugar
