"""Reentrenamiento automático del modelo KNN (componente pendiente del
Objetivo Específico 2).

A diferencia de scripts/06_entrenar_modelo.py (pensado para correrse a
mano durante el desarrollo, con datos sintéticos y el dataset exportado
a CSV), este servicio vive dentro del propio backend: se dispara solo,
usando directamente las valoraciones reales acumuladas en PostgreSQL, sin
pasar por ningún archivo intermedio.

Dos decisiones de diseño, declaradas explícitamente:
  - Umbral de disparo: se reentrena solo si hay al menos
    UMBRAL_VALORACIONES_NUEVAS valoraciones reales nuevas desde el último
    entrenamiento activo (no en cada petición, ni con cada valoración
    nueva una por una) — evita reentrenar por una sola fila y gastar CPU
    sin necesidad real.
  - Activación condicionada a la calidad: el modelo nuevo se activa
    automáticamente solo si su Precision@K es al menos igual a la del
    modelo vigente. Si sale peor (posible con pocos datos todavía), se
    guarda registrado mismo, para trazabilidad, pero NO reemplaza al que
    ya está sirviendo producción.
"""

import os
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.conexion import engine
from app.models.modelos_ml import ModeloML
from app.models.valoraciones import Valoracion

UMBRAL_VALORACIONES_NUEVAS = 5
PUNTUACION_MINIMA_RELEVANTE = 4
K = 5
SEMILLA = 42
FRACCION_PRUEBA = 0.2

CARPETA_MODELOS = os.path.join(os.path.dirname(__file__), "..", "ml", "modelos")


def _obtener_modelo_activo(db: Session) -> ModeloML | None:
    return (
        db.query(ModeloML)
        .filter(ModeloML.tipo == "knn", ModeloML.activo.is_(True))
        .order_by(ModeloML.fecha_entrenamiento.desc())
        .first()
    )


def _contar_valoraciones_nuevas(db: Session, desde: datetime | None) -> int:
    consulta = db.query(func.count(Valoracion.id)).filter(
        Valoracion.lugar_id.isnot(None), Valoracion.es_sintetico.is_(False)
    )
    if desde is not None:
        consulta = consulta.filter(Valoracion.fecha > desde)
    return consulta.scalar() or 0


def _cargar_catalogo() -> pd.DataFrame:
    return pd.read_sql(
        """
        SELECT l.id AS lugar_id, c.slug AS categoria_slug,
               COALESCE(l.precio, 0) AS precio,
               COALESCE(l.duracion_estimada_min, 60) AS duracion_estimada_min,
               l.accesible_movilidad_reducida
        FROM lugares l
        JOIN categorias c ON c.id = l.categoria_id
        WHERE l.activo = true
        """,
        engine,
    )


def _cargar_valoraciones_reales() -> pd.DataFrame:
    return pd.read_sql(
        """
        SELECT v.usuario_id AS usuario_hash, v.lugar_id, v.puntuacion
        FROM valoraciones v
        WHERE v.lugar_id IS NOT NULL AND v.es_sintetico = false
        """,
        engine,
    )


def _construir_matriz(lugares: pd.DataFrame) -> tuple[np.ndarray, float, float]:
    categorias_dummy = pd.get_dummies(lugares["categoria_slug"], prefix="cat")
    precio_max = lugares["precio"].max() or 1
    duracion_max = lugares["duracion_estimada_min"].max() or 1
    caracteristicas = pd.concat(
        [
            categorias_dummy,
            (lugares["precio"] / precio_max).rename("precio_norm"),
            (lugares["duracion_estimada_min"] / duracion_max).rename("duracion_norm"),
            lugares["accesible_movilidad_reducida"].astype(int).rename("accesible"),
        ],
        axis=1,
    )
    return caracteristicas.values.astype(float), precio_max, duracion_max


def _dividir_entrenamiento_prueba(valoraciones: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(SEMILLA)
    filas_entrenamiento, filas_prueba = [], []
    for _, grupo in valoraciones.groupby("usuario_hash"):
        if len(grupo) < 2:
            filas_entrenamiento.extend(grupo.index.tolist())
            continue
        indices = grupo.index.to_numpy().copy()
        rng.shuffle(indices)
        cantidad_prueba = max(1, round(len(indices) * FRACCION_PRUEBA))
        indices_prueba = set(indices[:cantidad_prueba])
        for indice in indices:
            (filas_prueba if indice in indices_prueba else filas_entrenamiento).append(indice)
    return valoraciones.loc[filas_entrenamiento], valoraciones.loc[filas_prueba]


def _precision_en_k(recomendados: list[int], relevantes: set[int], k: int) -> float:
    aciertos = len(set(recomendados[:k]) & relevantes)
    return aciertos / k


def _evaluar_precision(
    modelo_knn: NearestNeighbors,
    matriz: np.ndarray,
    lugar_id_por_fila: list[int],
    entrenamiento_le_gusto: dict,
    entrenamiento_visto: dict,
    prueba_relevante: dict,
) -> tuple[float, int]:
    fila_por_lugar = {lugar_id: fila for fila, lugar_id in enumerate(lugar_id_por_fila)}
    precisiones = []

    for usuario_hash, relevantes in prueba_relevante.items():
        if not relevantes:
            continue
        le_gusto = entrenamiento_le_gusto.get(usuario_hash, [])
        filas_interes = [fila_por_lugar[lid] for lid in le_gusto if lid in fila_por_lugar]
        if not filas_interes:
            continue

        perfil = matriz[filas_interes].mean(axis=0, keepdims=True)
        _, vecinos = modelo_knn.kneighbors(perfil, n_neighbors=len(matriz))
        excluir = entrenamiento_visto.get(usuario_hash, set())

        recomendados = []
        for fila in vecinos[0]:
            lugar_id = lugar_id_por_fila[fila]
            if lugar_id in excluir:
                continue
            recomendados.append(lugar_id)
            if len(recomendados) == K:
                break

        if recomendados:
            precisiones.append(_precision_en_k(recomendados, relevantes, K))

    precision = round(float(np.mean(precisiones)), 4) if precisiones else 0.0
    return precision, len(precisiones)


def reentrenar_si_corresponde(db: Session, forzar: bool = False) -> dict:
    """Punto de entrada único. Revisa si corresponde reentrenar (o lo
    fuerza si forzar=True, para poder probarlo desde el panel de
    administrador sin esperar a acumular valoraciones nuevas) y, de ser
    el caso, entrena, evalúa y decide si activar el modelo resultante.

    Siempre devuelve un dict explicando qué pasó (nunca None), para que
    el endpoint administrativo pueda mostrarlo directamente.
    """
    modelo_activo = _obtener_modelo_activo(db)
    desde = modelo_activo.fecha_entrenamiento if modelo_activo else None
    nuevas = _contar_valoraciones_nuevas(db, desde)

    if not forzar and nuevas < UMBRAL_VALORACIONES_NUEVAS:
        return {
            "entrenado": False,
            "motivo": (
                f"Solo hay {nuevas} valoraciones reales nuevas desde el último entrenamiento "
                f"activo; se necesitan al menos {UMBRAL_VALORACIONES_NUEVAS} para disparar un "
                f"reentrenamiento automático."
            ),
            "valoraciones_nuevas": nuevas,
        }

    valoraciones = _cargar_valoraciones_reales()
    if valoraciones.empty:
        return {"entrenado": False, "motivo": "Todavía no hay valoraciones reales en la base de datos."}

    entrenamiento, prueba = _dividir_entrenamiento_prueba(valoraciones)
    if entrenamiento.empty or prueba.empty:
        return {
            "entrenado": False,
            "motivo": (
                "No hay suficientes usuarios con 2 o más valoraciones reales todavía para armar "
                "un conjunto de entrenamiento y otro de prueba."
            ),
        }

    lugares = _cargar_catalogo()
    if lugares.empty:
        return {"entrenado": False, "motivo": "El catálogo de lugares activos está vacío."}

    matriz, precio_max, duracion_max = _construir_matriz(lugares)
    lugar_id_por_fila = lugares["lugar_id"].tolist()

    entrenamiento_le_gusto = (
        entrenamiento[entrenamiento["puntuacion"] >= PUNTUACION_MINIMA_RELEVANTE]
        .groupby("usuario_hash")["lugar_id"]
        .apply(list)
        .to_dict()
    )
    entrenamiento_visto = entrenamiento.groupby("usuario_hash")["lugar_id"].apply(set).to_dict()
    prueba_relevante = (
        prueba[prueba["puntuacion"] >= PUNTUACION_MINIMA_RELEVANTE]
        .groupby("usuario_hash")["lugar_id"]
        .apply(set)
        .to_dict()
    )

    modelo_knn = NearestNeighbors(n_neighbors=min(15, len(matriz)), metric="cosine")
    modelo_knn.fit(matriz)

    precision_nueva, usuarios_evaluados = _evaluar_precision(
        modelo_knn, matriz, lugar_id_por_fila, entrenamiento_le_gusto, entrenamiento_visto, prueba_relevante
    )
    precision_vigente = (
        (modelo_activo.metricas or {}).get("knn_contenido", {}).get("precision_at_k", 0.0)
        if modelo_activo
        else 0.0
    )

    os.makedirs(CARPETA_MODELOS, exist_ok=True)
    version_nueva = f"auto-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    ruta_modelo = os.path.join(CARPETA_MODELOS, f"recomendador_knn_{version_nueva}.joblib")
    joblib.dump(
        {
            "modelo_knn": modelo_knn,
            "matriz_caracteristicas": matriz,
            "lugar_id_por_fila": lugar_id_por_fila,
            "precio_max": precio_max,
            "duracion_max": duracion_max,
            "version": version_nueva,
            "fecha_entrenamiento": datetime.now(timezone.utc).isoformat(),
        },
        ruta_modelo,
    )

    activar = precision_nueva >= precision_vigente
    registro = ModeloML(
        nombre="Recomendador KNN de contenido (reentrenamiento automático)",
        version=version_nueva,
        tipo="knn",
        metricas={
            "knn_contenido": {
                "precision_at_k": precision_nueva,
                "k": K,
                "usuarios_evaluados": usuarios_evaluados,
            }
        },
        ruta_archivo=os.path.abspath(ruta_modelo),
        fecha_entrenamiento=datetime.now(timezone.utc),
        activo=False,
    )
    db.add(registro)
    db.flush()

    if activar:
        db.query(ModeloML).filter(ModeloML.tipo == "knn", ModeloML.activo.is_(True)).update(
            {"activo": False}
        )
        registro.activo = True

    db.commit()

    return {
        "entrenado": True,
        "activado": activar,
        "version": version_nueva,
        "precision_nueva": precision_nueva,
        "precision_anterior": precision_vigente,
        "usuarios_evaluados": usuarios_evaluados,
        "valoraciones_nuevas_consideradas": nuevas,
        "motivo": (
            "Activado: igualó o superó la precisión del modelo vigente."
            if activar
            else "Entrenado pero NO activado: su precisión quedó por debajo del modelo vigente."
        ),
    }
