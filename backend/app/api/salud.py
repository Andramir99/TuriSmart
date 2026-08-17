"""Endpoint de salud: GET /salud.

Sirve para que el frontend (o cualquier herramienta de monitoreo) pueda
confirmar que la API está viva y respondiendo, sin necesidad de tocar la
base de datos ni ninguna lógica de negocio.
"""

from fastapi import APIRouter

router = APIRouter(tags=["Salud"])


@router.get("/salud")
def verificar_salud():
    return {"estado": "ok", "servicio": "TuriSmart Lima API"}
