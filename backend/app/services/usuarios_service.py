"""Lógica de negocio de usuarios: crear cuenta, autenticar, actualizar.

Vive separada de app/api/auth.py y app/api/usuarios.py a propósito: los
archivos de app/api/ solo deben encargarse de HTTP (leer el request,
devolver la respuesta con el código correcto). Si mañana la misma lógica
hace falta desde otro lugar (un script, un job en segundo plano), se
importa esta función sin arrastrar nada de FastAPI.
"""

from sqlalchemy.orm import Session

from app.core.seguridad import hash_contrasena, verificar_contrasena
from app.models.usuarios import Usuario
from app.schemas.usuarios import UsuarioRegistro


def obtener_por_correo(db: Session, correo: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.correo == correo).first()


def obtener_por_id(db: Session, usuario_id: int) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()


def crear_usuario(db: Session, datos: UsuarioRegistro) -> Usuario:
    usuario = Usuario(
        nombre=datos.nombre,
        correo=datos.correo,
        contrasena_hash=hash_contrasena(datos.contrasena),
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)  # trae el id y fecha_registro que puso la base de datos
    return usuario


def establecer_nueva_contrasena(db: Session, usuario: Usuario, nueva_contrasena: str) -> None:
    usuario.contrasena_hash = hash_contrasena(nueva_contrasena)
    db.commit()


def autenticar_usuario(db: Session, correo: str, contrasena: str) -> Usuario | None:
    """Devuelve el usuario si el correo existe y la contraseña es correcta.
    Devuelve None en cualquier otro caso (correo inexistente, contraseña
    incorrecta, o cuenta desactivada) — a propósito no se distingue cuál
    de esas tres cosas pasó: decírselo a quien intenta entrar ayudaría a
    un atacante a saber qué correos SÍ están registrados.
    """
    usuario = obtener_por_correo(db, correo)
    if not usuario or not usuario.activo:
        return None
    if not verificar_contrasena(contrasena, usuario.contrasena_hash):
        return None
    return usuario
