from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.categorias import CategoriaPublica


class LugarPublico(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None
    descripcion_corta: str | None
    categoria: CategoriaPublica
    distrito: str
    direccion: str | None
    precio: float | None
    horario: str | None
    duracion_estimada_min: int | None
    tipo_turismo: str | None
    nivel_popularidad: int
    servicios_disponibles: list[str] | None
    recomendaciones_visitante: str | None
    lat: float
    lon: float
    accesible_movilidad_reducida: bool
    imagen_url: str | None
    etiquetas: list[str] | None
    valoracion_promedio: float
    total_valoraciones: int
    fuente_informacion: str | None
    fecha_actualizacion: datetime
