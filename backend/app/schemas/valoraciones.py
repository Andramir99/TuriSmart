from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ValoracionEntrada(BaseModel):
    lugar_id: int | None = None
    itinerario_id: int | None = None
    puntuacion: int = Field(ge=1, le=5)
    recomendacion_util: bool | None = None
    estado_visita: str | None = Field(default=None, pattern="^(visitado|descartado|pendiente)$")
    comentario: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validar_referencia_unica(self):
        # Se valora UN lugar o UN itinerario, nunca los dos a la vez ni
        # ninguno — si no, "puntuacion" no tendría a qué aplicarse.
        if bool(self.lugar_id) == bool(self.itinerario_id):
            raise ValueError(
                "Indica exactamente uno: lugar_id o itinerario_id (no ambos, no ninguno)."
            )
        return self


class ValoracionPublica(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lugar_id: int | None
    itinerario_id: int | None
    puntuacion: int
    recomendacion_util: bool | None
    estado_visita: str | None
    comentario: str | None
    fecha: datetime
