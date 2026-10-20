"""Importa todos los modelos en un solo lugar.

Esto tiene un motivo técnico concreto: cada modelo referencia a otros por
su nombre de clase como texto (por ejemplo Mapped["Usuario"] dentro de
Perfil). Para que SQLAlchemy pueda resolver esos nombres, TODAS las
clases deben haberse importado antes de usarlas. Alembic (las
migraciones) importa este archivo para "ver" el esquema completo.
"""

from app.models.categorias import Categoria
from app.models.encuestas import Encuesta, RespuestaEncuesta
from app.models.interacciones import Interaccion
from app.models.itinerarios import DetalleItinerario, Itinerario
from app.models.lugares import Lugar
from app.models.modelos_ml import ModeloML
from app.models.perfiles import Perfil
from app.models.preferencias import Preferencia, PreferenciaCategoria
from app.models.recomendaciones import Recomendacion
from app.models.solicitudes_arco import SolicitudArco
from app.models.usuarios import Usuario
from app.models.valoraciones import Valoracion

__all__ = [
    "Categoria",
    "DetalleItinerario",
    "Encuesta",
    "Interaccion",
    "Itinerario",
    "Lugar",
    "ModeloML",
    "Perfil",
    "Preferencia",
    "PreferenciaCategoria",
    "Recomendacion",
    "RespuestaEncuesta",
    "SolicitudArco",
    "Usuario",
    "Valoracion",
]
