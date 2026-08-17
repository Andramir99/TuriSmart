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
    dentro_de_distancia = True

    coordenadas_origen = DISTRITOS_COORDS.get(distrito_partida) if distrito_partida else None
    if coordenadas_origen:
        distancia_km = calcular_distancia_km(*coordenadas_origen, lugar.lat, lugar.lon)
        limite = distancia_maxima_km or 15.0
        if distancia_km <= limite:
            puntaje_distancia = 1.0 - (distancia_km / limite) * 0.5  # entre 0.5 y 1.0
        else:
            puntaje_distancia = max(0.0, 0.5 - (distancia_km - limite) / limite)
            # margen de tolerancia: no lo descartamos de plano por pasarse
            # un poco, solo penalizamos su puntaje.
            dentro_de_distancia = distancia_km <= limite * 1.5

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
        "dentro_de_distancia": dentro_de_distancia,
    }


def _construir_motivo(lugar: Lugar, presupuesto: str, distrito_partida: str | None, info: dict) -> str:
    clausulas = []
    if info["coincide_categoria"]:
        clausulas.append(f"coincide con tu interés en {lugar.categoria.nombre.lower()}")
    if info["coincide_presupuesto"]:
        clausulas.append(f"está dentro de tu presupuesto {presupuesto}")
    if info["distancia_km"] is not None:
        clausulas.append(f"se encuentra a {info['distancia_km']:.1f} km de {distrito_partida}")

    if not clausulas:
        return f"{lugar.nombre} es uno de los lugares mejor valorados del catálogo."

    if len(clausulas) == 1:
        cuerpo = clausulas[0]
    else:
        cuerpo = ", ".join(clausulas[:-1]) + " y " + clausulas[-1]

    return f"Te recomendamos {lugar.nombre} porque {cuerpo}."


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
    limite: int = 5,
) -> list[dict]:
    lugares = db.query(Lugar).options(joinedload(Lugar.categoria)).filter(Lugar.activo.is_(True)).all()
    categorias_preferidas = set(datos.categorias)

    candidatos = []
    for lugar in lugares:
        info = _puntuar_lugar(
            lugar, categorias_preferidas, datos.presupuesto, datos.distrito_partida, datos.distancia_maxima_km
        )
        if not info["dentro_de_distancia"]:
            continue
        motivo = _construir_motivo(lugar, datos.presupuesto, datos.distrito_partida, info)
        candidatos.append({"lugar": lugar, "puntuacion": info["puntaje_total"], "motivo": motivo})

    candidatos.sort(key=lambda item: item["puntuacion"], reverse=True)
    mejores = candidatos[:limite]

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
