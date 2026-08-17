"""Lógica de negocio de itinerarios: crear (con validaciones), listar los
propios, ver el detalle de uno, eliminarlo.
"""

from datetime import date as date_type
from datetime import datetime, timedelta

from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.geografia import distancia_km
from app.models.itinerarios import DetalleItinerario, Itinerario
from app.models.lugares import Lugar
from app.schemas.itinerarios import ItinerarioEntrada, ItinerarioResumen, ParadaEntrada

# Si una parada no trae "duracion_min" pero sí "hora_inicio", asumimos
# esta duración para poder revisar cruces de horario con la siguiente.
DURACION_POR_DEFECTO_MIN = 60

# El catálogo no incluye comida, transporte ni imprevistos, así que el
# presupuesto máximo estimado es el costo de entradas más un margen.
MARGEN_PRESUPUESTO_MAXIMO = 1.4


def _validar_horarios(paradas_por_dia: dict[int, list[ParadaEntrada]], lugares_por_id: dict[int, Lugar]) -> None:
    """Revisa, día por día, que ninguna parada empiece antes de que
    termine la anterior. Solo compara paradas que SÍ tienen hora_inicio
    ("cuando existan datos disponibles", como pide el enunciado) — si el
    usuario no puso horarios, no hay nada que validar.
    """
    for dia_numero, paradas in paradas_por_dia.items():
        con_horario = sorted(
            (parada for parada in paradas if parada.hora_inicio is not None),
            key=lambda parada: parada.hora_inicio,
        )
        for anterior, siguiente in zip(con_horario, con_horario[1:]):
            duracion = anterior.duracion_min or DURACION_POR_DEFECTO_MIN
            fin_anterior = (
                datetime.combine(date_type.today(), anterior.hora_inicio) + timedelta(minutes=duracion)
            ).time()
            if siguiente.hora_inicio < fin_anterior:
                nombre_anterior = lugares_por_id[anterior.lugar_id].nombre
                nombre_siguiente = lugares_por_id[siguiente.lugar_id].nombre
                raise ValueError(
                    f"Conflicto de horario el día {dia_numero}: "
                    f"'{nombre_anterior}' ({anterior.hora_inicio.strftime('%H:%M')} + {duracion} min) "
                    f"se cruza con '{nombre_siguiente}' ({siguiente.hora_inicio.strftime('%H:%M')})."
                )


def crear_itinerario(db: Session, usuario_id: int, datos: ItinerarioEntrada) -> Itinerario:
    lugar_ids = {parada.lugar_id for parada in datos.paradas}
    lugares = db.query(Lugar).filter(Lugar.id.in_(lugar_ids), Lugar.activo.is_(True)).all()
    lugares_por_id = {lugar.id: lugar for lugar in lugares}

    faltantes = lugar_ids - lugares_por_id.keys()
    if faltantes:
        raise ValueError(f"Lugar(es) no encontrado(s) en el catálogo: {sorted(faltantes)}")

    paradas_por_dia: dict[int, list[ParadaEntrada]] = {}
    for parada in datos.paradas:
        paradas_por_dia.setdefault(parada.dia_numero, []).append(parada)

    _validar_horarios(paradas_por_dia, lugares_por_id)

    # Costo total: suma del precio de entrada de cada parada.
    costo_total = sum(float(lugares_por_id[parada.lugar_id].precio or 0) for parada in datos.paradas)

    # Distancia estimada: suma de la distancia en línea recta entre
    # paradas consecutivas DEL MISMO DÍA (no tiene sentido sumar la
    # distancia entre el último lugar de un día y el primero del
    # siguiente, son recorridos separados).
    distancia_total = 0.0
    for paradas_dia in paradas_por_dia.values():
        lugares_dia = [lugares_por_id[parada.lugar_id] for parada in paradas_dia]
        for origen, destino in zip(lugares_dia, lugares_dia[1:]):
            distancia_total += distancia_km(origen.lat, origen.lon, destino.lat, destino.lon)

    itinerario = Itinerario(
        usuario_id=usuario_id,
        titulo=datos.titulo,
        fecha_inicio=datos.fecha_inicio,
        dias=max(paradas_por_dia.keys()),
        presupuesto=datos.presupuesto,
        tipo_grupo=datos.tipo_grupo,
        presupuesto_estimado_min=round(costo_total, 2),
        presupuesto_estimado_max=round(costo_total * MARGEN_PRESUPUESTO_MAXIMO, 2),
        distancia_estimada_km=round(distancia_total, 2),
        recomendacion_ia=datos.recomendacion_ia,
        generado_por_ia=True,
    )
    db.add(itinerario)
    db.flush()  # asigna itinerario.id sin cerrar la transacción

    for dia_numero, paradas_dia in paradas_por_dia.items():
        # El "orden" dentro del día lo decide la posición en la lista que
        # mandó el cliente — así el frontend no tiene que llevar la
        # cuenta de números de orden, solo mandar las paradas en el
        # orden en que quiere que aparezcan.
        for orden, parada in enumerate(paradas_dia, start=1):
            db.add(
                DetalleItinerario(
                    itinerario_id=itinerario.id,
                    lugar_id=parada.lugar_id,
                    dia_numero=dia_numero,
                    orden=orden,
                    hora_inicio=parada.hora_inicio,
                    duracion_min=parada.duracion_min,
                    nota=parada.nota,
                )
            )

    db.commit()
    db.refresh(itinerario)
    return itinerario


def listar_mios(db: Session, usuario_id: int) -> list[ItinerarioResumen]:
    itinerarios = (
        db.query(Itinerario)
        .options(selectinload(Itinerario.detalles))
        .filter(Itinerario.usuario_id == usuario_id)
        .order_by(Itinerario.fecha_creacion.desc())
        .all()
    )
    return [
        ItinerarioResumen(
            id=itinerario.id,
            titulo=itinerario.titulo,
            fecha_inicio=itinerario.fecha_inicio,
            dias=itinerario.dias,
            presupuesto=itinerario.presupuesto,
            tipo_grupo=itinerario.tipo_grupo,
            total_lugares=len(itinerario.detalles),
            fecha_creacion=itinerario.fecha_creacion,
        )
        for itinerario in itinerarios
    ]


def obtener_por_id(db: Session, itinerario_id: int, usuario_id: int) -> Itinerario | None:
    # El filtro por usuario_id no es solo un detalle: evita que alguien
    # vea el itinerario de otra persona adivinando el id en la URL.
    return (
        db.query(Itinerario)
        .options(
            selectinload(Itinerario.detalles)
            .joinedload(DetalleItinerario.lugar)
            .joinedload(Lugar.categoria)
        )
        .filter(Itinerario.id == itinerario_id, Itinerario.usuario_id == usuario_id)
        .first()
    )


def eliminar(db: Session, itinerario: Itinerario) -> None:
    db.delete(itinerario)
    db.commit()
