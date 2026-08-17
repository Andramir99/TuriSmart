from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

TIPOS_INTERACCION = "vista|clic|agregado_itinerario|recomendacion_aceptada|recomendacion_rechazada"


class InteraccionEntrada(BaseModel):
    lugar_id: int | None = None
    itinerario_id: int | None = None
    tipo_interaccion: str = Field(pattern=f"^({TIPOS_INTERACCION})$")
    metadatos: dict | None = None


class InteraccionPublica(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lugar_id: int | None
    itinerario_id: int | None
    tipo_interaccion: str
    fecha: datetime
