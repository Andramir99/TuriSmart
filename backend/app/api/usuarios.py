"""Endpoints del propio usuario autenticado: GET /usuarios/me y
PUT /usuarios/me. Ambos son rutas privadas: exigen un token válido
mediante Depends(obtener_usuario_actual).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencias import obtener_usuario_actual
from app.core.seguridad import verificar_contrasena
from app.database.conexion import get_db
from app.models.usuarios import Usuario
from app.schemas.usuarios import CambiarContrasenaEntrada, MensajeRespuesta, UsuarioActualizar, UsuarioPublico
from app.services import usuarios_service

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


@router.put("/me/contrasena", response_model=MensajeRespuesta)
def cambiar_mi_contrasena(
    datos: CambiarContrasenaEntrada,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    if not verificar_contrasena(datos.contrasena_actual, usuario.contrasena_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual no es correcta.",
        )

    usuarios_service.establecer_nueva_contrasena(db, usuario, datos.nueva_contrasena)
    return MensajeRespuesta(mensaje="Contraseña actualizada correctamente.")
