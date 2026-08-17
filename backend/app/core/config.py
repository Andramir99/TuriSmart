"""Configuración central del backend.

Todo lo que puede cambiar entre tu máquina, la de un compañero, o el
servidor de producción (URLs, contraseñas, orígenes permitidos) vive en
variables de entorno, nunca escrito directamente en el código. Este
archivo las lee una sola vez y las deja disponibles como un objeto
"Settings" que el resto del backend puede importar.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TuriSmart Lima API"
    app_env: str = "development"

    # Dominios desde los que el navegador puede llamar a esta API.
    # En .env se escriben separados por comas (ver cors_origins_list).
    cors_origins: str = "http://localhost:5173"

    # Se usa desde la Etapa 5 (conexión a PostgreSQL/PostGIS). Por ahora
    # queda vacío: nada en esta etapa lee este valor todavía.
    database_url: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origen.strip() for origen in self.cors_origins.split(",") if origen.strip()]


@lru_cache
def get_settings() -> Settings:
    # @lru_cache hace que Settings() se construya (y el .env se lea) una
    # sola vez por proceso, no en cada request.
    return Settings()
