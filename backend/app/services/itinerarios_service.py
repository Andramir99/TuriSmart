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

    # Costo total: suma del precio de entrada de cada parada, multiplicado
    # por la cantidad de personas del grupo (cada una paga su entrada) —
    # observación real del sponsor Nelson: "familia" puede ser 3, 4 o 5
    # personas, y el presupuesto no era realista si no se contaba eso.
    costo_total = sum(
        float(lugares_por_id[parada.lugar_id].precio or 0) for parada in datos.paradas
    ) * datos.numero_personas

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
        numero_personas=datos.numero_personas,
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


def _recalcular_totales(itinerario: Itinerario) -> None:
    """Recalcula presupuesto y distancia estimados tras agregar o quitar
    una parada suelta — misma fórmula que crear_itinerario, pero a partir
    de las paradas que YA quedaron guardadas en vez de datos de entrada.
    """
    paradas_por_dia: dict[int, list[DetalleItinerario]] = {}
    for detalle in itinerario.detalles:
        paradas_por_dia.setdefault(detalle.dia_numero, []).append(detalle)

    costo_total = sum(float(d.lugar.precio or 0) for d in itinerario.detalles) * itinerario.numero_personas

    distancia_total = 0.0
    for detalles_dia in paradas_por_dia.values():
        detalles_ordenados = sorted(detalles_dia, key=lambda d: d.orden)
        for origen, destino in zip(detalles_ordenados, detalles_ordenados[1:]):
            distancia_total += distancia_km(origen.lugar.lat, origen.lugar.lon, destino.lugar.lat, destino.lugar.lon)

    itinerario.presupuesto_estimado_min = round(costo_total, 2)
    itinerario.presupuesto_estimado_max = round(costo_total * MARGEN_PRESUPUESTO_MAXIMO, 2)
    itinerario.distancia_estimada_km = round(distancia_total, 2)
    if paradas_por_dia:
        itinerario.dias = max(itinerario.dias, max(paradas_por_dia.keys()))


def agregar_parada(db: Session, itinerario: Itinerario, datos: ParadaEntrada) -> DetalleItinerario:
    """Agrega UN lugar suelto a un itinerario ya existente (a diferencia
    de crear_itinerario, que arma uno nuevo completo desde el asistente
    de Planificar). Es lo que usa el botón "Agregar a mi itinerario" de
    la ficha de un destino.
    """
    lugar = db.query(Lugar).filter(Lugar.id == datos.lugar_id, Lugar.activo.is_(True)).first()
    if lugar is None:
        raise ValueError(f"Lugar {datos.lugar_id} no encontrado en el catálogo.")

    orden_maximo = max(
        (d.orden for d in itinerario.detalles if d.dia_numero == datos.dia_numero), default=0
    )
    detalle = DetalleItinerario(
        itinerario_id=itinerario.id,
        lugar_id=datos.lugar_id,
        dia_numero=datos.dia_numero,
        orden=orden_maximo + 1,
        hora_inicio=datos.hora_inicio,
        duracion_min=datos.duracion_min,
        nota=datos.nota,
    )
    db.add(detalle)
    db.flush()
    itinerario.detalles.append(detalle)
    _recalcular_totales(itinerario)
    db.commit()
    db.refresh(detalle)
    return detalle


def eliminar_parada(db: Session, itinerario: Itinerario, parada_id: int) -> None:
    parada = next((detalle for detalle in itinerario.detalles if detalle.id == parada_id), None)
    if parada is None:
        raise ValueError(f"La parada {parada_id} no pertenece a este itinerario.")

    itinerario.detalles.remove(parada)
    db.delete(parada)
    _recalcular_totales(itinerario)
    db.commit()


def renombrar(db: Session, itinerario: Itinerario, nuevo_titulo: str) -> Itinerario:
    itinerario.titulo = nuevo_titulo
    db.commit()
    db.refresh(itinerario)
    return itinerario


def marcar_parada_visitada(db: Session, itinerario: Itinerario, parada_id: int, visitado: bool) -> DetalleItinerario:
    parada = next((detalle for detalle in itinerario.detalles if detalle.id == parada_id), None)
    if parada is None:
        raise ValueError(f"La parada {parada_id} no pertenece a este itinerario.")

    parada.visitado = visitado
    db.commit()
    db.refresh(parada)
    return parada


def reordenar_paradas(db: Session, itinerario: Itinerario, dia_numero: int, orden_ids: list[int]) -> None:
    paradas_del_dia = {detalle.id: detalle for detalle in itinerario.detalles if detalle.dia_numero == dia_numero}

    if set(orden_ids) != set(paradas_del_dia.keys()):
        raise ValueError(
            "La lista de reordenamiento debe incluir exactamente las paradas del día "
            f"{dia_numero}, ni más ni menos."
        )

    # Se pasa por un rango temporal (negativo) antes de asignar el orden
    # final: si se escribiera el orden definitivo de una sola vez, en
    # algún punto intermedio dos filas compartirían el mismo (itinerario_id,
    # dia_numero, orden), violando la restricción única "uq_detalle_orden_por_dia"
    # antes de que la transacción termine de aplicar todos los cambios.
    for indice, parada_id in enumerate(orden_ids, start=1):
        paradas_del_dia[parada_id].orden = -indice
    db.flush()
    for indice, parada_id in enumerate(orden_ids, start=1):
        paradas_del_dia[parada_id].orden = indice
    db.commit()
