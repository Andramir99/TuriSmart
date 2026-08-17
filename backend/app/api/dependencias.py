"""Dependencias de FastAPI reutilizables entre endpoints.

"obtener_usuario_actual" es la pieza que protege una ruta privada: se usa
así en cualquier endpoint futuro:

    @router.get("/algo-privado")
    def ver_algo(usuario: Usuario = Depends(obtener_usuario_actual)):
        ...

FastAPI ejecuta esta función ANTES que el cuerpo del endpoint. Si el
token falta, es inválido, expiró, o el usuario ya no existe/está
desactivado, esta función lanza un 401 y el código del endpoint ni
siquiera llega a ejecutarse.
"""

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.seguridad import decodificar_token
from app.database.conexion import get_db
from app.models.usuarios import Usuario
from app.services.usuarios_service import obtener_por_id

# tokenUrl es solo informativo (para que /docs sepa dónde pedir el token
# al usar el botón "Authorize"); el login real vive en POST /auth/login.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# auto_error=False: si no hay token, NO lanza 401 — simplemente devuelve
# None. Se usa en endpoints como POST /encuestas, que funcionan tanto para
# alguien anónimo como para alguien con sesión iniciada (y en ese segundo
# caso, la encuesta queda asociada a su cuenta).
oauth2_scheme_opcional = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la sesión",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decodificar_token(token)
        usuario_id = int(payload.get("sub"))
    except (jwt.PyJWTError, TypeError, ValueError):
        raise credenciales_invalidas

    usuario = obtener_por_id(db, usuario_id)
    if usuario is None or not usuario.activo:
        raise credenciales_invalidas

    return usuario


def obtener_usuario_opcional(
    token: str | None = Depends(oauth2_scheme_opcional),
    db: Session = Depends(get_db),
) -> Usuario | None:
    if not token:
        return None
    try:
        payload = decodificar_token(token)
        usuario = obtener_por_id(db, int(payload.get("sub")))
    except (jwt.PyJWTError, TypeError, ValueError):
        return None

    if usuario is None or not usuario.activo:
        return None
    return usuario
