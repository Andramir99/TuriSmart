"""Recomendador INICIAL basado en contenido y reglas (Etapa 9).

Importante para la tesis: esto NO es Machine Learning todavía. Es una
fórmula fija que compara las preferencias del usuario contra cada lugar
del catálogo y les da un puntaje. Sirve para el problema del "usuario
nuevo" (sin historial todavía no hay nada que un modelo pueda aprender).
El modelo de ML de verdad se entrena en la Etapa 14 con datos que este
mismo recomendador, junto con las valoraciones (Etapa 12), va generando
mientras tanto.

Cómo puntúa cada lugar (pesos en PESO_CATEGORIA/PRESUPUESTO/DISTANCIA):
  - 50%: ¿el lugar es de una categoría que el usuario marcó como interés?
  - 30%: ¿el precio del lugar entra en su presupuesto?
  - 20%: ¿qué tan cerca está de su distrito de partida?
  - + un pequeño extra según qué tan bien valorado está el lugar en general.
"""

from sqlalchemy.orm import Session, joinedload

from app.core.geografia import distancia_km as calcular_distancia_km
from app.models.lugares import Lugar
from app.models.modelos_ml import ModeloML
from app.models.recomendaciones import Recomendacion
from app.schemas.recomendaciones import RecomendacionEntrada

PESO_CATEGORIA = 0.5
PESO_PRESUPUESTO = 0.3
PESO_DISTANCIA = 0.2

PRECIO_MAXIMO_POR_PRESUPUESTO = {
    "economico": 20.0,
    "moderado": 60.0,
    "premium": 10_000.0,
}

# Centros aproximados de cada distrito, para poder calcular una distancia
# aunque el catálogo todavía no tenga la ubicación exacta de partida del
# usuario (eso requeriría geolocalización real, fuera del alcance actual).
DISTRITOS_COORDS = {
    "Cercado de Lima": (-12.0464, -77.0428),
    "Barranco": (-12.1494, -77.0203),
    "Miraflores": (-12.1211, -77.0324),
    "San Isidro": (-12.0970, -77.0350),
    "San Borja": (-12.1083, -77.0000),
    "Surco": (-12.1350, -76.9900),
    "La Molina": (-12.0800, -76.9300),
    "Pueblo Libre": (-12.0733, -77.0717),
    "Jesús María": (-12.0733, -77.0483),
    "Lince": (-12.0850, -77.0350),
    "San Miguel": (-12.0770, -77.0917),
    "Magdalena del Mar": (-12.0917, -77.0700),
    "Chorrillos": (-12.1750, -77.0167),
    "Rímac": (-12.0333, -77.0283),
    "Pachacamac": (-12.2333, -76.8500),
    "Lurín": (-12.2750, -76.8700),
    "Comas": (-11.9500, -77.0500),
    "Los Olivos": (-11.9700, -77.0700),
    "San Juan de Lurigancho": (-11.9900, -77.0100),
    "Ate": (-12.0333, -76.9167),
}


def _puntuar_lugar(
    lugar: Lugar,
    categorias_preferidas: set[str],
    presupuesto: str,
    distrito_partida: str | None,
    distancia_maxima_km: float | None,
) -> dict:
    coincide_categoria = lugar.categoria.slug in categorias_preferidas
    puntaje_categoria = 1.0 if coincide_categoria else 0.15

    precio_maximo = PRECIO_MAXIMO_POR_PRESUPUESTO.get(presupuesto, 60.0)
    precio_lugar = float(lugar.precio or 0)
    coincide_presupuesto = precio_lugar <= precio_maximo
    puntaje_presupuesto = 1.0 if coincide_presupuesto else max(0.0, 1 - (precio_lugar - precio_maximo) / precio_maximo)

    distancia_km = None
    puntaje_distancia = 0.5  # neutral si no sabemos de dónde parte
    limite = distancia_maxima_km or 15.0
    dentro_del_limite_declarado = True

    coordenadas_origen = DISTRITOS_COORDS.get(distrito_partida) if distrito_partida else None
    if coordenadas_origen:
        distancia_km = calcular_distancia_km(*coordenadas_origen, lugar.lat, lugar.lon)
        if distancia_km <= limite:
            puntaje_distancia = 1.0 - (distancia_km / limite) * 0.5  # entre 0.5 y 1.0
        else:
            puntaje_distancia = max(0.0, 0.5 - (distancia_km - limite) / limite)
            dentro_del_limite_declarado = False

    puntaje_total = (
        PESO_CATEGORIA * puntaje_categoria
        + PESO_PRESUPUESTO * puntaje_presupuesto
        + PESO_DISTANCIA * puntaje_distancia
        + float(lugar.valoracion_promedio or 0) / 50  # pequeño extra, máx. 0.1
    )

    return {
        "puntaje_total": min(1.0, puntaje_total),
        "coincide_categoria": coincide_categoria,
        "coincide_presupuesto": coincide_presupuesto,
        "distancia_km": distancia_km,
        "limite_km": limite,
        "dentro_del_limite_declarado": dentro_del_limite_declarado,
    }


def _etiqueta_distancia(info: dict) -> str | None:
    """'cerca' / 'moderada' / 'lejos', para que el frontend muestre una
    etiqueta clara en vez de dejar la distancia escondida en un párrafo.
    None si no hay distrito de partida (no hay con qué comparar).
    """
    distancia_km = info["distancia_km"]
    if distancia_km is None:
        return None
    limite = info["limite_km"]
    if distancia_km <= limite:
        return "cerca"
    if distancia_km <= limite * 2:
        return "moderada"
    return "lejos"


MEDIO_TRANSPORTE_ETIQUETA = {
    "a_pie": "a pie",
    "transporte_publico": "en transporte público",
    "auto_taxi": "en auto o taxi",
}

# A partir de cuántos km caminar deja de ser razonable para un turista
# promedio. No es una medición real (eso requeriría datos del turista:
# edad, condición física, etc.), es un umbral honesto y simple.
DISTANCIA_MAXIMA_RAZONABLE_A_PIE_KM = 2.0


def _construir_motivo(
    lugar: Lugar,
    presupuesto: str,
    distrito_partida: str | None,
    info: dict,
    medio_transporte: str = "cualquiera",
    movilidad_reducida: bool = False,
) -> str:
    clausulas = []
    if info["coincide_categoria"]:
        clausulas.append(f"coincide con tu interés en {lugar.categoria.nombre.lower()}")
    if info["coincide_presupuesto"]:
        clausulas.append(f"está dentro de tu presupuesto {presupuesto}")
    if info["distancia_km"] is not None and info["dentro_del_limite_declarado"]:
        clausulas.append(f"se encuentra a {info['distancia_km']:.1f} km de {distrito_partida}")

    if not clausulas:
        base = f"{lugar.nombre} es uno de los lugares mejor valorados del catálogo."
    elif len(clausulas) == 1:
        base = f"Te recomendamos {lugar.nombre} porque {clausulas[0]}."
    else:
        cuerpo = ", ".join(clausulas[:-1]) + " y " + clausulas[-1]
        base = f"Te recomendamos {lugar.nombre} porque {cuerpo}."

    # Transparencia honesta: si está lejos, se lo decimos en vez de
    # callarlo — se sigue recomendando por sus otras cualidades, pero el
    # usuario debe saber que implica más tiempo de traslado.
    if info["distancia_km"] is not None and not info["dentro_del_limite_declarado"]:
        base += (
            f" Eso sí: está a {info['distancia_km']:.1f} km de {distrito_partida}, "
            f"más lejos de lo que preferiste — considera el tiempo de traslado."
        )

    # Advertencia de medio de transporte (Wu, reunión 27/08): no calculamos
    # una ruta real, solo avisamos cuando la distancia declarada no es
    # razonable para el medio elegido, en vez de dejar al turista adivinar.
    distancia_km = info["distancia_km"]
    if medio_transporte == "a_pie" and distancia_km is not None and distancia_km > DISTANCIA_MAXIMA_RAZONABLE_A_PIE_KM:
        base += (
            f" Considerando que prefieres trasladarte a pie, {distancia_km:.1f} km puede ser "
            f"una distancia considerable — te sugerimos transporte público o taxi para este tramo."
        )
    elif medio_transporte in MEDIO_TRANSPORTE_ETIQUETA and distancia_km is not None:
        base += f" Trasladarte {MEDIO_TRANSPORTE_ETIQUETA[medio_transporte]} hasta aquí es una opción razonable."

    # Accesibilidad (Wu, reunión 27/08): nunca se descarta un lugar por
    # esto, solo se hace explícito para que el turista decida con
    # información completa, igual que con la distancia.
    if movilidad_reducida:
        if lugar.accesible_movilidad_reducida:
            base += " Este lugar está señalado como accesible para movilidad reducida."
        else:
            base += (
                " Ten en cuenta que este lugar todavía no está señalado como accesible "
                "para movilidad reducida en nuestro catálogo."
            )

    return base


def _obtener_o_crear_modelo_reglas(db: Session) -> ModeloML:
    modelo = db.query(ModeloML).filter(ModeloML.tipo == "reglas").first()
    if modelo is not None:
        return modelo

    modelo = ModeloML(
        nombre="Recomendador inicial basado en reglas",
        version="1.0",
        tipo="reglas",
        activo=True,
    )
    db.add(modelo)
    db.commit()
    db.refresh(modelo)
    return modelo


def generar_recomendaciones(
    db: Session,
    usuario_id: int | None,
    datos: RecomendacionEntrada,
) -> list[dict]:
    lugares = db.query(Lugar).options(joinedload(Lugar.categoria)).filter(Lugar.activo.is_(True)).all()
    categorias_preferidas = set(datos.categorias)

    # A propósito NO se descarta ningún lugar por estar lejos: con un
    # catálogo chico (24 lugares concentrados en el centro/sur de Lima),
    # excluir candidatos por distancia podía dejar 0-2 resultados para
    # distritos alejados (ej. Comas, San Juan de Lurigancho) — y entonces
    # un itinerario de "3 días" terminaba con apenas 2 lugares, porque
    # sencillamente no había suficientes candidatos para repartir. La
    # distancia influye en el PUNTAJE (más lejos, puntúa más bajo) y se
    # informa con una etiqueta clara, pero nunca descarta un candidato.
    candidatos = []
    for lugar in lugares:
        info = _puntuar_lugar(
            lugar, categorias_preferidas, datos.presupuesto, datos.distrito_partida, datos.distancia_maxima_km
        )
        motivo = _construir_motivo(
            lugar,
            datos.presupuesto,
            datos.distrito_partida,
            info,
            medio_transporte=datos.medio_transporte,
            movilidad_reducida=datos.movilidad_reducida,
        )
        candidatos.append(
            {
                "lugar": lugar,
                "puntuacion": info["puntaje_total"],
                "motivo": motivo,
                "distancia_km": round(info["distancia_km"], 1) if info["distancia_km"] is not None else None,
                "distancia_etiqueta": _etiqueta_distancia(info),
            }
        )

    candidatos.sort(key=lambda item: item["puntuacion"], reverse=True)
    # datos.cantidad lo calcula el frontend según los días del viaje (ej.
    # 3 lugares/día), para que alcancen lugares distintos para cada día.
    mejores = candidatos[: datos.cantidad]

    # Cada recomendación que se le muestra al usuario queda registrada.
    # Es la materia prima de "recomendaciones aceptadas o rechazadas" que
    # se completa en la Etapa 12 y que alimentará al modelo de ML real.
    modelo = _obtener_o_crear_modelo_reglas(db)
    for item in mejores:
        db.add(
            Recomendacion(
                usuario_id=usuario_id,
                lugar_id=item["lugar"].id,
                modelo_id=modelo.id,
                puntuacion=round(item["puntuacion"], 4),
                motivo=item["motivo"],
            )
        )
    db.commit()

    return mejores
