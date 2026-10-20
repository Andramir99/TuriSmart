from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SolicitudArcoEntrada(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    correo: EmailStr
    tipo_solicitud: str = Field(pattern="^(acceso|rectificacion|cancelacion|oposicion)$")
    mensaje: str = Field(min_length=5, max_length=2000)


class SolicitudArcoPublica(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo_solicitud: str
    fecha_creacion: datetime
