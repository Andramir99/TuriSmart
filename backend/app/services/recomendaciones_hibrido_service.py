"""Recomendador híbrido "Recomendados para ti" (Etapa 16).

A diferencia de POST /recomendaciones (reglas, a partir de un formulario)
y POST /recomendaciones/ml (KNN offline, solo valoraciones >= 4), este
combina el perfil dinámico calculado en perfil_dinamico_service —que
aprende de búsquedas, filtros, clics, tiempo de lectura, me gusta e
itinerarios— con la popularidad del lugar, y mezcla una porción de
exploración para no encerrar al usuario en una sola categoría (burbuja
de recomendaciones).

No reemplaza al KNN offline: cuando hay un modelo de ML activo y el
usuario tiene valoraciones >=4, su similitud se sopesa junto con el
perfil dinámico en vez de ignorarse.
"""

import random

from sqlalchemy.orm import Session, joinedload

from app.ml.pesos_interacciones import FRASE_POR_SENAL
from app.models.interacciones import Interaccion
from app.models.lugares import Lugar
from app.models.modelos_ml import ModeloML
from app.models.recomendaciones import Recomendacion
from app.models.valoraciones import Valoracion
from app.services import perfil_dinamico_service, recomendaciones_ml_service

# Lugares con alguna de estas interacciones ya son "conocidos" para el
# usuario: no tiene sentido recomendárselos de nuevo en "para ti".
TIPOS_QUE_EXCLUYEN_DE_RECOMENDACIONES = ("agregado_itinerario", "marcado_visitado")

# % de las recomendaciones reservado a "descubrimiento": lugares de
# categorías con poca o ninguna señal en el perfil del usuario. Punto 11
# del pedido ("no crear una burbuja de recomendaciones").
PROPORCION_EXPLORACION = 0.2

PESO_PERFIL_DINAMICO = 0.65
PESO_MODELO_KNN = 0.20
PESO_POPULARIDAD = 0.15

PUNTAJE_BASE_SIN_SENAL = 0.05


def _obtener_o_crear_modelo_hibrido(db: Session) -> ModeloML:
    modelo = db.query(ModeloML).filter(ModeloML.tipo == "hibrido").first()
    if modelo is not None:
        return modelo
    modelo = ModeloML(
        nombre="Recomendador híbrido (perfil dinámico + KNN + popularidad)",
        version="1.0",
        tipo="hibrido",
        activo=True,
    )
    db.add(modelo)
    db.commit()
    db.refresh(modelo)
    return modelo


def _motivo(categoria_nombre: str, categoria_slug: str, senal: str | None, es_exploracion: bool) -> str:
    if es_exploracion:
        return "Popular entre viajeros con intereses similares — para que descubras algo distinto a lo habitual."
    if senal and senal in FRASE_POR_SENAL:
        return FRASE_POR_SENAL[senal].format(categoria=categoria_nombre.lower())
    return f"Podría interesarte: coincide con tu interés en {categoria_nombre.lower()}."


def generar_recomendaciones_para_ti(db: Session, usuario_id: int, cantidad: int = 10) -> list[dict]:
    perfil = perfil_dinamico_service.calcular_perfil(db, usuario_id)

    # KNN offline: si hay modelo activo y el usuario ya tiene valoraciones
    # >=4, reusamos su puntaje de similitud como una señal más (no
    # reemplaza al perfil dinámico, lo complementa).
    puntajes_knn: dict[int, float] = {}
    try:
        for item in recomendaciones_ml_service.generar_recomendaciones_ml(db, usuario_id, k=100):
            puntajes_knn[item["lugar"].id] = item["puntuacion"]
    except ValueError:
        pass  # sin modelo activo o sin valoraciones suficientes: se sigue sin ese término

    ya_valorados = {
        v.lugar_id
        for v in db.query(Valoracion).filter(Valoracion.usuario_id == usuario_id, Valoracion.lugar_id.isnot(None))
    }
    ya_conocidos = {
        ia.lugar_id
        for ia in db.query(Interaccion).filter(
            Interaccion.usuario_id == usuario_id,
            Interaccion.lugar_id.isnot(None),
            Interaccion.tipo_interaccion.in_(TIPOS_QUE_EXCLUYEN_DE_RECOMENDACIONES),
        )
    }
    excluidos = ya_valorados | ya_conocidos

    lugares = (
        db.query(Lugar)
        .options(joinedload(Lugar.categoria))
        .filter(Lugar.activo.is_(True), ~Lugar.id.in_(excluidos) if excluidos else True)
        .all()
    )

    candidatos = []
    sin_perfil = not perfil
    for lugar in lugares:
        slug = lugar.categoria.slug
        info_categoria = perfil.get(slug)
        score_contenido = info_categoria.puntaje if info_categoria else PUNTAJE_BASE_SIN_SENAL
        score_knn = puntajes_knn.get(lugar.id, 0.0)
        score_popularidad = (lugar.nivel_popularidad / 5) * 0.6 + (float(lugar.valoracion_promedio or 0) / 5) * 0.4

        if sin_perfil:
            # Cold start real (sección 7 del pedido): sin interacciones
            # todavía, la popularidad manda.
            puntaje = score_popularidad
        else:
            puntaje = (
                PESO_PERFIL_DINAMICO * score_contenido
                + PESO_MODELO_KNN * score_knn
                + PESO_POPULARIDAD * score_popularidad
            )

        candidatos.append(
            {
                "lugar": lugar,
                "puntaje": puntaje,
                "slug": slug,
                "senal": info_categoria.senal_dominante() if info_categoria else None,
                "tiene_senal": info_categoria is not None and info_categoria.puntaje > 0,
            }
        )

    candidatos.sort(key=lambda c: c["puntaje"], reverse=True)

    if sin_perfil:
        # Sin historial: variedad entre categorías en vez de solo lo más
        # popular en general (evita que "cultural", la categoría con más
        # lugares en el catálogo, cope toda la lista).
        por_categoria: dict[str, list[dict]] = {}
        for c in candidatos:
            por_categoria.setdefault(c["slug"], []).append(c)
        resultado, i = [], 0
        categorias_ciclo = list(por_categoria.keys())
        while len(resultado) < min(cantidad, len(candidatos)) and categorias_ciclo:
            slug = categorias_ciclo[i % len(categorias_ciclo)]
            bucket = por_categoria[slug]
            if bucket:
                resultado.append(bucket.pop(0))
            else:
                categorias_ciclo.remove(slug)
                continue
            i += 1
        seleccionados = [(c, True) for c in resultado]
    else:
        n_exploracion = max(1, round(cantidad * PROPORCION_EXPLORACION))
        n_explotacion = max(0, cantidad - n_exploracion)

        explotacion = [c for c in candidatos if c["tiene_senal"]][:n_explotacion]
        if len(explotacion) < n_explotacion:
            # perfil con pocas categorías con señal: completa con lo mejor puntuado restante
            usados = {c["lugar"].id for c in explotacion}
            for c in candidatos:
                if len(explotacion) >= n_explotacion:
                    break
                if c["lugar"].id not in usados:
                    explotacion.append(c)
                    usados.add(c["lugar"].id)

        usados = {c["lugar"].id for c in explotacion}
        categorias_en_explotacion = {c["slug"] for c in explotacion}
        candidatos_exploracion = [
            c for c in candidatos if c["lugar"].id not in usados and c["slug"] not in categorias_en_explotacion
        ]
        if not candidatos_exploracion:
            candidatos_exploracion = [c for c in candidatos if c["lugar"].id not in usados]
        random.shuffle(candidatos_exploracion)
        exploracion = candidatos_exploracion[:n_exploracion]

        seleccionados = [(c, False) for c in explotacion] + [(c, True) for c in exploracion]
        random.shuffle(seleccionados)

    resultados = []
    for c, es_exploracion in seleccionados:
        lugar = c["lugar"]
        resultados.append(
            {
                "lugar": lugar,
                "puntuacion": round(min(1.0, c["puntaje"]), 4),
                "motivo": _motivo(lugar.categoria.nombre, c["slug"], c["senal"], es_exploracion or sin_perfil),
                "distancia_km": None,
                "distancia_etiqueta": None,
            }
        )

    modelo = _obtener_o_crear_modelo_hibrido(db)
    for item in resultados:
        db.add(
            Recomendacion(
                usuario_id=usuario_id,
                lugar_id=item["lugar"].id,
                modelo_id=modelo.id,
                puntuacion=item["puntuacion"],
                motivo=item["motivo"],
            )
        )
    db.commit()

    return resultados
