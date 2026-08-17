from pydantic import BaseModel, ConfigDict


class CategoriaPublica(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    nombre: str
    descripcion: str | None
    icono: str | None
