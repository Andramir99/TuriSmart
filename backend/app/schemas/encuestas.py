from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class EncuestaEntrada(BaseModel):
    # True obligatorio: sin consentimiento, la encuesta no debería usarse
    # para entrenar nada (ver Etapa 13). Lo validamos también aquí, no
    # solo en la interfaz, porque el frontend no es la única forma en la
    # que alguien podría llamar a este endpoint.
    consentimiento_datos: bool
    version_encuesta: str = "1.0"
    # pregunta -> respuesta, ej: {"presupuesto": "moderado", "categorias_interes": "cultural,natural"}
    respuestas: dict[str, str]

    @field_validator("consentimiento_datos")
    @classmethod
    def exigir_consentimiento(cls, valor: bool) -> bool:
        if not valor:
            raise ValueError(
                "Se necesita tu consentimiento para guardar la encuesta de forma anonimizada."
            )
        return valor


class EncuestaPublica(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    consentimiento_datos: bool
    version_encuesta: str
    fecha_creacion: datetime
