"""Endpoints del propio usuario autenticado: GET /usuarios/me y
PUT /usuarios/me. Ambos son rutas privadas: exigen un token válido
mediante Depends(obtener_usuario_actual).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencias import obtener_usuario_actual
from app.database.conexion import get_db
from app.models.usuarios import Usuario
from app.schemas.usuarios import UsuarioActualizar, UsuarioPublico

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/me", response_model=UsuarioPublico)
def ver_mi_perfil(usuario: Usuario = Depends(obtener_usuario_actual)):
    return usuario


@router.put("/me", response_model=UsuarioPublico)
def actualizar_mi_perfil(
    datos: UsuarioActualizar,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    if datos.nombre is not None:
        usuario.nombre = datos.nombre
        db.commit()
        db.refresh(usuario)

    return usuario
