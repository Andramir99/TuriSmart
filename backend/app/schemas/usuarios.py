"""Esquemas Pydantic de usuarios.

Los modelos de app/models/ definen las tablas (lo que hay en PostgreSQL).
Los esquemas de aquí definen los JSON que la API recibe y devuelve —
son cosas distintas a propósito: por ejemplo, UsuarioPublico jamás
incluye "contrasena_hash", aunque la tabla usuarios sí tenga esa columna.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioRegistro(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    correo: EmailStr
    contrasena: str = Field(min_length=8, max_length=72)


class UsuarioLogin(BaseModel):
    correo: EmailStr
    contrasena: str


class UsuarioActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=120)


class UsuarioPublico(BaseModel):
    # from_attributes=True permite construir este esquema directamente
    # desde un objeto Usuario de SQLAlchemy (usuario.nombre, usuario.id...)
    # en vez de tener que armar un diccionario a mano en cada endpoint.
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    correo: EmailStr
    rol: str
    fecha_registro: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class OlvideContrasenaEntrada(BaseModel):
    correo: EmailStr


class OlvideContrasenaRespuesta(BaseModel):
    mensaje: str
    # Modo prototipo: el proyecto no tiene un servidor de correo
    # configurado (ver README), así que en vez de enviarse por email el
    # enlace de restablecimiento se devuelve acá mismo para que el
    # frontend lo muestre en pantalla. None cuando el correo no existe
    # (no se revela si una cuenta existe o no).
    token: str | None = None


class RestablecerContrasenaEntrada(BaseModel):
    token: str
    nueva_contrasena: str = Field(min_length=8, max_length=72)


class MensajeRespuesta(BaseModel):
    mensaje: str
