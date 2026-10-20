"""Analítica para agencias y entidades (Objetivo Específico 4).

A diferencia del panel de la Etapa 3 (datos de ejemplo fijos en
dashboardMock.js), estas consultas se calculan en vivo sobre
interacciones, valoraciones e itinerarios reales.

Todo lo que se agrega aquí EXCLUYE a propósito los datos sintéticos
(scripts/03_generar_datos_sinteticos.py): son 150 cuentas de prueba que
inflarían artificialmente cualquier métrica si se mezclaran con el uso
real de la plataforma. Por eso, con pocos usuarios reales todavía, los
números pueden verse chicos — es preferible mostrar la verdad a inflar
el panel con datos de prueba disfrazados de reales.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.categorias import Categoria
from app.models.interacciones import Interaccion
from app.models.itinerarios import DetalleItinerario, Itinerario
from app.models.lugares import Lugar
from app.models.solicitudes_arco import SolicitudArco
from app.models.usuarios import Usuario
from app.models.valoraciones import Valoracion

SEMANAS_TENDENCIA = 6

COLOR_POR_GRUPO = {
    "solo": "#7b3fb8",
    "pareja": "#d9822b",
    "familia": "#2e7d32",
    "amigos": "#3355cc",
}
ETIQUETA_POR_GRUPO = {
    "solo": "Viajes solo",
    "pareja": "Viajes en pareja",
    "familia": "Viajes en familia",
    "amigos": "Viajes con amigos",
}
COLORES_AVATAR = ["#c1443c", "#d9822b", "#3355cc", "#2e7d32", "#7b3fb8"]


def _nombre_mostrable(nombre_completo: str) -> str:
    # "María García" -> "María G.": suficiente para identificar la fila sin
    # exponer el nombre completo de nadie en un panel semi-público.
    partes = nombre_completo.strip().split()
    if len(partes) == 1:
        return partes[0]
    return f"{partes[0]} {partes[-1][0]}."


def _con_tz(fecha: datetime) -> datetime:
    return fecha if fecha.tzinfo is not None else fecha.replace(tzinfo=timezone.utc)


def _contar_por_semana(fechas: list[datetime], inicio: datetime, semanas: int) -> list[int]:
    """Agrupa una lista de fechas en "semanas desde inicio" (semana 0, 1,
    2...), usada tanto por la tendencia de consultas/itinerarios como por
    la de usuarios nuevos del panel de administración.
    """
    conteo = [0] * semanas
    for fecha in fechas:
        dias = (_con_tz(fecha) - inicio).days
        conteo[max(0, min(semanas - 1, dias // 7))] += 1
    return conteo


def obtener_estadisticas_generales(db: Session) -> dict:
    total_itinerarios = db.query(Itinerario).join(Usuario).filter(Usuario.es_sintetico.is_(False)).count()

    promedio_valoracion = (
        db.query(func.avg(Valoracion.puntuacion)).filter(Valoracion.es_sintetico.is_(False)).scalar()
    )

    fila_destino_top = (
        db.query(Lugar.nombre, func.count(Valoracion.id).label("total"))
        .join(Valoracion, Valoracion.lugar_id == Lugar.id)
        .filter(Valoracion.es_sintetico.is_(False))
        .group_by(Lugar.id)
        .order_by(func.count(Valoracion.id).desc())
        .first()
    )

    aceptadas = (
        db.query(Interaccion)
        .filter(Interaccion.tipo_interaccion == "recomendacion_aceptada", Interaccion.es_sintetico.is_(False))
        .count()
    )
    rechazadas = (
        db.query(Interaccion)
        .filter(Interaccion.tipo_interaccion == "recomendacion_rechazada", Interaccion.es_sintetico.is_(False))
        .count()
    )
    total_reacciones = aceptadas + rechazadas

    return {
        "total_itinerarios": total_itinerarios,
        "promedio_valoracion": round(float(promedio_valoracion), 2) if promedio_valoracion is not None else None,
        "destino_mas_valorado": fila_destino_top[0] if fila_destino_top else None,
        "destino_mas_valorado_total": fila_destino_top[1] if fila_destino_top else 0,
        "tasa_aceptacion_recomendaciones": (
            round(aceptadas / total_reacciones * 100, 1) if total_reacciones else None
        ),
        "total_reacciones_recomendaciones": total_reacciones,
    }


def obtener_tendencia_semanal(db: Session, semanas: int = SEMANAS_TENDENCIA) -> dict:
    inicio = datetime.now(timezone.utc) - timedelta(weeks=semanas)

    fechas_interacciones = (
        db.query(Interaccion.fecha).filter(Interaccion.fecha >= inicio, Interaccion.es_sintetico.is_(False)).all()
    )
    fechas_itinerarios = (
        db.query(Itinerario.fecha_creacion)
        .join(Usuario)
        .filter(Itinerario.fecha_creacion >= inicio, Usuario.es_sintetico.is_(False))
        .all()
    )

    return {
        "etiquetas": [f"Sem {i + 1}" for i in range(semanas)],
        "consultas": _contar_por_semana([f for (f,) in fechas_interacciones], inicio, semanas),
        "itinerarios": _contar_por_semana([f for (f,) in fechas_itinerarios], inicio, semanas),
    }


def obtener_destinos_mas_vistos(db: Session, limite: int = 7) -> list[dict]:
    filas = (
        db.query(Lugar.nombre, func.count(Interaccion.id).label("total"))
        .join(Interaccion, Interaccion.lugar_id == Lugar.id)
        .filter(Interaccion.tipo_interaccion == "vista", Interaccion.es_sintetico.is_(False))
        .group_by(Lugar.id)
        .order_by(func.count(Interaccion.id).desc())
        .limit(limite)
        .all()
    )
    return [{"nombre": nombre, "valor": total} for nombre, total in filas]


def obtener_metricas_tipo_grupo(db: Session) -> list[dict]:
    filas = (
        db.query(Itinerario.tipo_grupo, func.count(Itinerario.id))
        .join(Usuario)
        .filter(Usuario.es_sintetico.is_(False))
        .group_by(Itinerario.tipo_grupo)
        .all()
    )
    total = sum(cantidad for _, cantidad in filas) or 1
    return [
        {
            "etiqueta": ETIQUETA_POR_GRUPO.get(tipo, tipo),
            "valor": round(cantidad / total * 100),
            "color": COLOR_POR_GRUPO.get(tipo, "#6f6b64"),
        }
        for tipo, cantidad in filas
    ]


def obtener_itinerarios_recientes(db: Session, limite: int = 5) -> list[dict]:
    itinerarios = (
        db.query(Itinerario)
        .join(Usuario)
        .options(
            selectinload(Itinerario.detalles).joinedload(DetalleItinerario.lugar),
            joinedload(Itinerario.usuario),
        )
        .filter(Usuario.es_sintetico.is_(False))
        .order_by(Itinerario.fecha_creacion.desc())
        .limit(limite)
        .all()
    )

    resultados = []
    for indice, itinerario in enumerate(itinerarios):
        satisfaccion = (
            db.query(func.avg(Valoracion.puntuacion)).filter(Valoracion.itinerario_id == itinerario.id).scalar()
        )
        resultados.append(
            {
                "id": itinerario.id,
                "usuario": _nombre_mostrable(itinerario.usuario.nombre),
                "color": COLORES_AVATAR[indice % len(COLORES_AVATAR)],
                "destinos": ", ".join(detalle.lugar.nombre for detalle in itinerario.detalles[:3]),
                "dias": itinerario.dias,
                "satisfaccion": round(float(satisfaccion), 1) if satisfaccion is not None else None,
                "fecha": itinerario.fecha_creacion.date().isoformat(),
            }
        )
    return resultados


# --- Panel general del administrador --------------------------------


def obtener_metricas_panel_admin(db: Session) -> dict:
    total_usuarios = db.query(Usuario).filter(Usuario.es_sintetico.is_(False)).count()
    total_lugares_activos = db.query(Lugar).filter(Lugar.activo.is_(True)).count()
    total_lugares_inactivos = db.query(Lugar).filter(Lugar.activo.is_(False)).count()
    total_itinerarios = db.query(Itinerario).join(Usuario).filter(Usuario.es_sintetico.is_(False)).count()

    valoracion_promedio_general = (
        db.query(func.avg(Valoracion.puntuacion)).filter(Valoracion.es_sintetico.is_(False)).scalar()
    )

    solicitudes_arco_pendientes = db.query(SolicitudArco).filter(SolicitudArco.atendida.is_(False)).count()

    return {
        "total_usuarios": total_usuarios,
        "total_lugares_activos": total_lugares_activos,
        "total_lugares_inactivos": total_lugares_inactivos,
        "total_itinerarios": total_itinerarios,
        "valoracion_promedio_general": (
            round(float(valoracion_promedio_general), 2) if valoracion_promedio_general is not None else None
        ),
        "solicitudes_arco_pendientes": solicitudes_arco_pendientes,
    }


def obtener_tendencia_semanal_administracion(db: Session, semanas: int = SEMANAS_TENDENCIA) -> dict:
    """Crecimiento de la plataforma semana a semana: cuentas reales nuevas
    e itinerarios reales nuevos — distinto de obtener_tendencia_semanal
    (esa mide "consultas", pensada para el Dashboard de agencias).
    """
    inicio = datetime.now(timezone.utc) - timedelta(weeks=semanas)

    fechas_usuarios = (
        db.query(Usuario.fecha_registro)
        .filter(Usuario.fecha_registro >= inicio, Usuario.es_sintetico.is_(False))
        .all()
    )
    fechas_itinerarios = (
        db.query(Itinerario.fecha_creacion)
        .join(Usuario)
        .filter(Itinerario.fecha_creacion >= inicio, Usuario.es_sintetico.is_(False))
        .all()
    )

    return {
        "etiquetas": [f"Sem {i + 1}" for i in range(semanas)],
        "usuarios_nuevos": _contar_por_semana([f for (f,) in fechas_usuarios], inicio, semanas),
        "itinerarios_nuevos": _contar_por_semana([f for (f,) in fechas_itinerarios], inicio, semanas),
    }


def obtener_lugares_por_categoria(db: Session) -> list[dict]:
    filas = (
        db.query(Categoria.nombre, func.count(Lugar.id))
        .join(Lugar, Lugar.categoria_id == Categoria.id)
        .filter(Lugar.activo.is_(True))
        .group_by(Categoria.id)
        .order_by(func.count(Lugar.id).desc())
        .all()
    )
    return [{"categoria": nombre, "cantidad": cantidad} for nombre, cantidad in filas]


def obtener_lugares_mejor_valorados(db: Session, limite: int = 5) -> list[dict]:
    filas = (
        db.query(Lugar.nombre, Lugar.valoracion_promedio, Lugar.total_valoraciones)
        .filter(Lugar.activo.is_(True), Lugar.total_valoraciones > 0)
        .order_by(Lugar.valoracion_promedio.desc(), Lugar.total_valoraciones.desc())
        .limit(limite)
        .all()
    )
    return [
        {"nombre": nombre, "valoracion_promedio": float(promedio), "total_valoraciones": total}
        for nombre, promedio, total in filas
    ]
