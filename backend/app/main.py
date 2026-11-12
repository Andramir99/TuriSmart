"""Punto de entrada del backend. Aquí se crea la aplicación FastAPI, se
configura qué orígenes pueden llamarla (CORS) y se registran los routers
de cada módulo (por ahora solo "salud"; en etapas siguientes se suman
auth, usuarios, lugares, itinerarios, etc.).

Se ejecuta con:  uvicorn app.main:app --reload   (desde la carpeta backend/)
"""

import asyncio
import contextlib
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    analitica,
    auth,
    categorias,
    encuestas,
    interacciones,
    itinerarios,
    lugares,
    preferencias,
    recomendaciones,
    salud,
    solicitudes_arco,
    usuarios,
    valoraciones,
)
from app.core.config import get_settings
from app.database.conexion import SessionLocal
from app.services import reentrenamiento_service

settings = get_settings()
logger = logging.getLogger("turismart.reentrenamiento")

# Cada cuántas horas se revisa si corresponde reentrenar el modelo KNN de
# forma automática (Objetivo Específico 2). No reentrena siempre que
# corre: solo si ya hay suficientes valoraciones reales nuevas desde el
# último entrenamiento activo (ver reentrenamiento_service).
INTERVALO_REENTRENAMIENTO_HORAS = 24


async def _ciclo_reentrenamiento_automatico() -> None:
    while True:
        await asyncio.sleep(INTERVALO_REENTRENAMIENTO_HORAS * 60 * 60)
        db = SessionLocal()
        try:
            resultado = reentrenamiento_service.reentrenar_si_corresponde(db)
            logger.info("Revisión de reentrenamiento automático: %s", resultado)
        except Exception:
            logger.exception("Falló la revisión de reentrenamiento automático")
        finally:
            db.close()


@contextlib.asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    tarea = asyncio.create_task(_ciclo_reentrenamiento_automatico())
    yield
    tarea.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await tarea


app = FastAPI(title=settings.app_name, lifespan=ciclo_de_vida)

# CORS: por defecto, un navegador bloquea que una página en localhost:5173
# (el frontend de React) llame a una API en localhost:8000 (este backend).
# Este middleware le dice al navegador que sí lo permita, solo para los
# orígenes listados en CORS_ORIGINS (ver app/core/config.py).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(salud.router)
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(categorias.router)
app.include_router(preferencias.router)
app.include_router(encuestas.router)
app.include_router(lugares.router)
app.include_router(recomendaciones.router)
app.include_router(itinerarios.router)
app.include_router(valoraciones.router)
app.include_router(interacciones.router)
app.include_router(solicitudes_arco.router)
app.include_router(analitica.router)
