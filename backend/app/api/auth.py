"""Endpoints de autenticación: POST /auth/registro y POST /auth/login."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.seguridad import crear_token_acceso
from app.database.conexion import get_db
from app.schemas.usuarios import Token, UsuarioLogin, UsuarioPublico, UsuarioRegistro
from app.services import usuarios_service

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/registro", response_model=UsuarioPublico, status_code=status.HTTP_201_CREATED)
def registrar_usuario(datos: UsuarioRegistro, db: Session = Depends(get_db)):
    if usuarios_service.obtener_por_correo(db, datos.correo):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta registrada con ese correo",
        )

    usuario = usuarios_service.crear_usuario(db, datos)
    return usuario


@router.post("/login", response_model=Token)
def iniciar_sesion(datos: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = usuarios_service.autenticar_usuario(db, datos.correo, datos.contrasena)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
        )

    token = crear_token_acceso(usuario.id, usuario.correo)
    return Token(access_token=token)
