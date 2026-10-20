"""Funciones puras de seguridad: hash de contraseñas y JWT.

No dependen de FastAPI ni de la base de datos a propósito — son fáciles
de probar solas y se pueden reutilizar desde cualquier parte del backend
(o desde un script de scripts/ si algún día hace falta).
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import get_settings

settings = get_settings()


def hash_contrasena(contrasena: str) -> str:
    """Convierte una contraseña en texto plano en un hash bcrypt.

    bcrypt genera una "sal" (salt) distinta cada vez, así que la MISMA
    contraseña produce un hash DIFERENTE cada vez que se llama a esta
    función — eso es intencional y necesario, no un bug.
    """
    hash_bytes = bcrypt.hashpw(contrasena.encode("utf-8"), bcrypt.gensalt())
    return hash_bytes.decode("utf-8")


def verificar_contrasena(contrasena: str, contrasena_hash: str) -> bool:
    """Compara una contraseña en texto plano contra un hash ya guardado."""
    return bcrypt.checkpw(contrasena.encode("utf-8"), contrasena_hash.encode("utf-8"))


def crear_token_acceso(usuario_id: int, correo: str) -> str:
    """Genera un JWT firmado que representa una sesión iniciada.

    "sub" (subject) es el estándar de JWT para identificar a quién
    pertenece el token; usamos el id del usuario. "exp" es la fecha de
    expiración: pasado ese momento, el token deja de ser válido aunque
    esté bien firmado.
    """
    expira = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expira_minutos)
    payload = {"sub": str(usuario_id), "correo": correo, "exp": expira}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algoritmo)


TIPO_TOKEN_RESTABLECIMIENTO = "restablecer_contrasena"
MINUTOS_VALIDEZ_RESTABLECIMIENTO = 30


def crear_token_restablecimiento(usuario_id: int, huella_contrasena_actual: str) -> str:
    """Token de un solo propósito (restablecer la contraseña), distinto
    del de sesión: dura mucho menos (30 min, no 1 día) y "tipo" en el
    payload evita que alguien use un token de sesión normal robado para
    entrar al endpoint de restablecimiento, o viceversa.

    "cf" (contraseña_hash, en el momento de pedir el restablecimiento)
    es lo que lo vuelve de un solo uso pese a ser un JWT sin estado en
    el servidor: en cuanto el restablecimiento se complete una vez, el
    hash de la contraseña cambia, así que ese mismo token ya no coincide
    la segunda vez (ver restablecer_contrasena en app/api/auth.py).
    """
    expira = datetime.now(timezone.utc) + timedelta(minutes=MINUTOS_VALIDEZ_RESTABLECIMIENTO)
    payload = {
        "sub": str(usuario_id),
        "tipo": TIPO_TOKEN_RESTABLECIMIENTO,
        "cf": huella_contrasena_actual,
        "exp": expira,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algoritmo)


def decodificar_token(token: str) -> dict:
    """Verifica la firma y la expiración de un token y devuelve su payload.

    Lanza jwt.PyJWTError (o una subclase, como ExpiredSignatureError) si
    el token es inválido, fue alterado, o ya expiró. Quien llame a esta
    función debe capturar esa excepción (ver app/api/dependencias.py).
    """
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algoritmo])
