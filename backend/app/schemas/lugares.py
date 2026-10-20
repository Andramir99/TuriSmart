from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

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


class LugarCrear(BaseModel):
    """Lo que un administrador manda al agregar un lugar nuevo al
    catálogo (POST /lugares). A diferencia de LugarPublico, acá
    "categoria_id" es un id crudo (no el objeto CategoriaPublica
    completo) y "lat"/"lon" son dos números sueltos — el backend arma
    la columna Geography a partir de ellos (ver lugares_service.crear).
    """

    nombre: str = Field(min_length=3, max_length=150)
    descripcion: str | None = None
    descripcion_corta: str | None = Field(default=None, max_length=200)
    categoria_id: int
    distrito: str = Field(min_length=2, max_length=80)
    direccion: str | None = None
    precio: float | None = Field(default=None, ge=0)
    horario: str | None = None
    duracion_estimada_min: int | None = Field(default=None, ge=0)
    tipo_turismo: str | None = None
    nivel_popularidad: int = Field(default=1, ge=1, le=5)
    servicios_disponibles: list[str] | None = None
    recomendaciones_visitante: str | None = None
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    accesible_movilidad_reducida: bool = False
    imagen_url: str | None = None
    etiquetas: list[str] | None = None
    fuente_informacion: str | None = None


class LugarActualizar(BaseModel):
    """Igual que LugarCrear, pero con todo opcional: PUT /lugares/{id}
    solo toca los campos que de verdad vengan en el cuerpo del request.
    """

    nombre: str | None = Field(default=None, min_length=3, max_length=150)
    descripcion: str | None = None
    descripcion_corta: str | None = Field(default=None, max_length=200)
    categoria_id: int | None = None
    distrito: str | None = Field(default=None, min_length=2, max_length=80)
    direccion: str | None = None
    precio: float | None = Field(default=None, ge=0)
    horario: str | None = None
    duracion_estimada_min: int | None = Field(default=None, ge=0)
    tipo_turismo: str | None = None
    nivel_popularidad: int | None = Field(default=None, ge=1, le=5)
    servicios_disponibles: list[str] | None = None
    recomendaciones_visitante: str | None = None
    lat: float | None = Field(default=None, ge=-90, le=90)
    lon: float | None = Field(default=None, ge=-180, le=180)
    accesible_movilidad_reducida: bool | None = None
    imagen_url: str | None = None
    etiquetas: list[str] | None = None
    fuente_informacion: str | None = None
