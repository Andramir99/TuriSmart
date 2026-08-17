"""Endpoint de salud: GET /salud.

Sirve para que el frontend (o cualquier herramienta de monitoreo) pueda
confirmar que la API está viva y respondiendo. Desde la Etapa 5 también
intenta una consulta mínima a PostgreSQL, para poder confirmar desde un
solo lugar que tanto el backend como la base de datos están bien.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.conexion import get_db

router = APIRouter(tags=["Salud"])


@router.get("/salud")
def verificar_salud(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        estado_base_datos = "conectada"
    except Exception:
        estado_base_datos = "sin conexión"

    return {
        "estado": "ok",
        "servicio": "TuriSmart Lima API",
        "base_datos": estado_base_datos,
    }
