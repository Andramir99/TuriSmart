"""Endpoints de autenticación: POST /auth/registro y POST /auth/login."""

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.seguridad import (
    TIPO_TOKEN_RESTABLECIMIENTO,
    crear_token_acceso,
    crear_token_restablecimiento,
    decodificar_token,
)
from app.database.conexion import get_db
from app.schemas.usuarios import (
    MensajeRespuesta,
    OlvideContrasenaEntrada,
    OlvideContrasenaRespuesta,
    RestablecerContrasenaEntrada,
    Token,
    UsuarioLogin,
    UsuarioPublico,
    UsuarioRegistro,
)
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


@router.post("/olvide-contrasena", response_model=OlvideContrasenaRespuesta)
def olvidar_contrasena(datos: OlvideContrasenaEntrada, db: Session = Depends(get_db)):
    mensaje = "Si existe una cuenta con ese correo, podrás continuar el restablecimiento."

    usuario = usuarios_service.obtener_por_correo(db, datos.correo)
    if usuario is None or not usuario.activo:
        # A propósito no se distingue esto de "sí existe": decirlo
        # ayudaría a un atacante a confirmar qué correos están
        # registrados (mismo criterio que autenticar_usuario).
        return OlvideContrasenaRespuesta(mensaje=mensaje)

    token = crear_token_restablecimiento(usuario.id, usuario.contrasena_hash)
    return OlvideContrasenaRespuesta(mensaje=mensaje, token=token)


@router.post("/restablecer-contrasena", response_model=MensajeRespuesta)
def restablecer_contrasena(datos: RestablecerContrasenaEntrada, db: Session = Depends(get_db)):
    enlace_invalido = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="El enlace de restablecimiento es inválido o ya venció. Solicita uno nuevo.",
    )

    try:
        payload = decodificar_token(datos.token)
        if payload.get("tipo") != TIPO_TOKEN_RESTABLECIMIENTO:
            raise enlace_invalido
        usuario_id = int(payload.get("sub"))
    except (jwt.PyJWTError, TypeError, ValueError):
        raise enlace_invalido

    usuario = usuarios_service.obtener_por_id(db, usuario_id)
    if usuario is None or not usuario.activo:
        raise enlace_invalido

    # Si la contraseña ya cambió desde que se pidió este enlace (porque
    # ya se usó una vez, o porque cambió por otra vía mientras tanto),
    # la huella guardada en el token ya no coincide: eso es lo que hace
    # que el enlace sea de un solo uso (ver crear_token_restablecimiento).
    if payload.get("cf") != usuario.contrasena_hash:
        raise enlace_invalido

    usuarios_service.establecer_nueva_contrasena(db, usuario, datos.nueva_contrasena)
    return MensajeRespuesta(mensaje="Contraseña actualizada. Ya puedes iniciar sesión.")
