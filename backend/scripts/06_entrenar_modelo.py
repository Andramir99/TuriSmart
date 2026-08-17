"""Etapa 14 — Entrena y evalúa un recomendador de Machine Learning real,
y lo compara contra una base de referencia simple (popularidad).

MODELOS COMPARADOS
  1) Popularidad: recomienda a TODO el mundo los lugares mejor valorados
     en promedio, sin importar quién es. Es la base de comparación
     estándar en sistemas de recomendación — cualquier modelo "de
     verdad" tiene que superarla para justificar su complejidad.
  2) KNN de contenido: arma un "perfil" por usuario (el promedio de las
     características de los lugares que calificó con 4-5 estrellas) y
     recomienda los lugares más parecidos a ese perfil (K vecinos más
     cercanos, scikit-learn), usando categoría, precio, duración y
     accesibilidad como características.

Ninguno de los dos es el recomendador por reglas de la Etapa 9 (ese usa
distancia geográfica en vivo, no se puede evaluar offline de la misma
forma) — la comparación real contra ese recomendador se hace con datos
de uso a medida que se acumulen (recomendaciones.fue_aceptada).

CÓMO SE EVALÚA (nunca solo "accuracy" — ver el enunciado de la tesis):
  - Precision@K: de las K recomendaciones, ¿qué fracción resultó ser un
    lugar que a esa persona sí le gustó (≥4 estrellas)?
  - Recall@K: de TODOS los lugares que a esa persona le gustaron, ¿qué
    fracción logró aparecer entre las K recomendaciones?
  - NDCG@K: como Precision@K, pero premia más si los aciertos aparecen
    primero en la lista (una recomendación acertada en el puesto 1 vale
    más que una en el puesto 5).

Para evaluar sin hacer trampa, a cada usuario se le esconde una parte de
sus valoraciones (conjunto de prueba) y el modelo se entrena solo con el
resto (conjunto de entrenamiento) — así medimos qué tan bien predice
lugares que el modelo NUNCA vio para esa persona.

Ejecutar desde backend/, con el entorno virtual activado:
    python scripts/06_entrenar_modelo.py

Requiere haber corrido antes:
    python scripts/04_preparar_dataset.py --incluir-sinteticos
"""

import json
import os
import sys
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import joblib  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.neighbors import NearestNeighbors  # noqa: E402

from app.database.conexion import SessionLocal, engine  # noqa: E402
from app.models.modelos_ml import ModeloML  # noqa: E402

SEMILLA = 42
K = 5  # "las 5 mejores recomendaciones", igual que en el resto de la app
PUNTUACION_MINIMA_RELEVANTE = 4  # 4 o 5 estrellas = "le gustó"
FRACCION_PRUEBA = 0.2

CARPETA_DATOS = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")
CARPETA_MODELOS = os.path.join(os.path.dirname(__file__), "..", "app", "ml", "modelos")
RUTA_MODELO = os.path.join(CARPETA_MODELOS, "recomendador_knn_v1.joblib")


# ---------------------------------------------------------------------
# 1) Cargar y preparar los datos
# ---------------------------------------------------------------------
def cargar_catalogo_de_lugares() -> pd.DataFrame:
    lugares = pd.read_sql(
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
    return lugares


def construir_matriz_de_caracteristicas(lugares: pd.DataFrame):
    """Convierte cada lugar en un vector numérico: una columna 0/1 por
    categoría (one-hot), precio y duración normalizados a 0-1, y
    accesibilidad como 0/1. Todas las columnas quedan en la misma
    escala aproximada para que ninguna "pese" más que otra en la
    distancia del KNN solo por tener números más grandes.
    """
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
    return caracteristicas.values.astype(float), list(caracteristicas.columns), precio_max, duracion_max


def dividir_entrenamiento_prueba(valoraciones: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Por cada usuario, esconde ~20% de sus valoraciones (mínimo 1) como
    prueba. Un usuario con una sola valoración no aporta nada a la
    evaluación (no queda nada de "entrenamiento" o nada que "esconder"),
    así que se descarta.
    """
    rng = np.random.default_rng(SEMILLA)
    filas_entrenamiento, filas_prueba = [], []

    for _, grupo in valoraciones.groupby("usuario_hash"):
        if len(grupo) < 2:
            continue
        indices = grupo.index.to_numpy().copy()
        rng.shuffle(indices)
        cantidad_prueba = max(1, round(len(indices) * FRACCION_PRUEBA))
        indices_prueba = set(indices[:cantidad_prueba])

        for indice in indices:
            (filas_prueba if indice in indices_prueba else filas_entrenamiento).append(indice)

    return valoraciones.loc[filas_entrenamiento], valoraciones.loc[filas_prueba]


# ---------------------------------------------------------------------
# 2) Los dos modelos
# ---------------------------------------------------------------------
def recomendar_por_popularidad(entrenamiento: pd.DataFrame, todos_los_lugares: list[int], k: int) -> list[int]:
    promedios = entrenamiento.groupby("lugar_id")["puntuacion"].mean().sort_values(ascending=False)
    return list(promedios.index[:k])


def entrenar_knn_contenido(matriz_caracteristicas: np.ndarray, k_vecinos: int = 15) -> NearestNeighbors:
    modelo = NearestNeighbors(n_neighbors=min(k_vecinos, len(matriz_caracteristicas)), metric="cosine")
    modelo.fit(matriz_caracteristicas)
    return modelo


def recomendar_por_contenido(
    modelo_knn: NearestNeighbors,
    matriz_caracteristicas: np.ndarray,
    lugar_id_por_fila: list[int],
    lugares_que_le_gustaron: list[int],
    lugares_a_excluir: set[int],
    k: int,
) -> list[int]:
    if not lugares_que_le_gustaron:
        return []

    fila_por_lugar = {lugar_id: fila for fila, lugar_id in enumerate(lugar_id_por_fila)}
    filas_de_interes = [fila_por_lugar[lid] for lid in lugares_que_le_gustaron if lid in fila_por_lugar]
    if not filas_de_interes:
        return []

    perfil_usuario = matriz_caracteristicas[filas_de_interes].mean(axis=0, keepdims=True)

    _, vecinos = modelo_knn.kneighbors(perfil_usuario, n_neighbors=len(matriz_caracteristicas))
    recomendados = []
    for fila in vecinos[0]:
        lugar_id = lugar_id_por_fila[fila]
        if lugar_id in lugares_a_excluir:
            continue
        recomendados.append(lugar_id)
        if len(recomendados) == k:
            break
    return recomendados


# ---------------------------------------------------------------------
# 3) Métricas — Precision@K, Recall@K, NDCG@K (nunca solo "accuracy")
# ---------------------------------------------------------------------
def precision_en_k(recomendados: list[int], relevantes: set[int], k: int) -> float:
    aciertos = len(set(recomendados[:k]) & relevantes)
    return aciertos / k


def recall_en_k(recomendados: list[int], relevantes: set[int], k: int) -> float:
    aciertos = len(set(recomendados[:k]) & relevantes)
    return aciertos / len(relevantes)


def ndcg_en_k(recomendados: list[int], relevantes: set[int], k: int) -> float:
    dcg = sum(1 / np.log2(posicion + 2) for posicion, lugar_id in enumerate(recomendados[:k]) if lugar_id in relevantes)
    idcg = sum(1 / np.log2(posicion + 2) for posicion in range(min(k, len(relevantes))))
    return dcg / idcg if idcg > 0 else 0.0


def evaluar_modelo(nombre: str, generar_recomendaciones_para_usuario, prueba_por_usuario: dict) -> dict:
    precisiones, recalls, ndcgs = [], [], []

    for usuario_hash, relevantes in prueba_por_usuario.items():
        if not relevantes:
            continue
        recomendados = generar_recomendaciones_para_usuario(usuario_hash)
        if not recomendados:
            continue
        precisiones.append(precision_en_k(recomendados, relevantes, K))
        recalls.append(recall_en_k(recomendados, relevantes, K))
        ndcgs.append(ndcg_en_k(recomendados, relevantes, K))

    metricas = {
        "precision_at_k": round(float(np.mean(precisiones)), 4) if precisiones else 0.0,
        "recall_at_k": round(float(np.mean(recalls)), 4) if recalls else 0.0,
        "ndcg_at_k": round(float(np.mean(ndcgs)), 4) if ndcgs else 0.0,
        "usuarios_evaluados": len(precisiones),
        "k": K,
    }
    print(f"-- {nombre} --")
    print(f"   Precision@{K}: {metricas['precision_at_k']:.3f}")
    print(f"   Recall@{K}:    {metricas['recall_at_k']:.3f}")
    print(f"   NDCG@{K}:      {metricas['ndcg_at_k']:.3f}")
    print(f"   (evaluado sobre {metricas['usuarios_evaluados']} usuarios con datos de prueba)")
    print()
    return metricas


# ---------------------------------------------------------------------
# 4) Orquestación
# ---------------------------------------------------------------------
def main():
    np.random.seed(SEMILLA)

    ruta_entrenamiento = os.path.join(CARPETA_DATOS, "dataset_entrenamiento.csv")
    if not os.path.exists(ruta_entrenamiento):
        print(f"No existe {ruta_entrenamiento}.")
        print("Corre primero: python scripts/04_preparar_dataset.py --incluir-sinteticos")
        return

    dataset = pd.read_csv(ruta_entrenamiento)
    valoraciones = dataset[dataset["tipo_evento"] == "valoracion"].dropna(subset=["usuario_hash", "lugar_id"]).copy()
    valoraciones["lugar_id"] = valoraciones["lugar_id"].astype(int)

    print(f"Valoraciones disponibles para entrenar/evaluar: {len(valoraciones)}")
    entrenamiento, prueba = dividir_entrenamiento_prueba(valoraciones)
    print(f"  Entrenamiento: {len(entrenamiento)} filas — Prueba: {len(prueba)} filas")
    print()

    if entrenamiento.empty or prueba.empty:
        print("No hay suficientes datos para entrenar y evaluar todavía.")
        print("Corre scripts/03_generar_datos_sinteticos.py para tener volumen de prueba.")
        return

    # ---- Catálogo completo y matriz de características ----
    lugares = cargar_catalogo_de_lugares()
    matriz, columnas, precio_max, duracion_max = construir_matriz_de_caracteristicas(lugares)
    lugar_id_por_fila = lugares["lugar_id"].tolist()

    # ---- "Le gustaron" (train) y "relevantes" (test) por usuario ----
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

    # ---- Modelo 1: Popularidad ----
    top_populares = recomendar_por_popularidad(entrenamiento, lugar_id_por_fila, k=len(lugar_id_por_fila))

    def recomendar_popularidad(usuario_hash):
        excluir = entrenamiento_visto.get(usuario_hash, set())
        return [lugar_id for lugar_id in top_populares if lugar_id not in excluir][:K]

    # ---- Modelo 2: KNN de contenido ----
    modelo_knn = entrenar_knn_contenido(matriz)

    def recomendar_knn(usuario_hash):
        return recomendar_por_contenido(
            modelo_knn,
            matriz,
            lugar_id_por_fila,
            entrenamiento_le_gusto.get(usuario_hash, []),
            entrenamiento_visto.get(usuario_hash, set()),
            K,
        )

    print("=" * 60)
    print("EVALUACIÓN (Precision@K, Recall@K, NDCG@K — nunca accuracy sola)")
    print("=" * 60)
    metricas_popularidad = evaluar_modelo("Popularidad (base de referencia)", recomendar_popularidad, prueba_relevante)
    metricas_knn = evaluar_modelo("KNN de contenido", recomendar_knn, prueba_relevante)

    mejora_precision = metricas_knn["precision_at_k"] - metricas_popularidad["precision_at_k"]
    print("=" * 60)
    print("EXPLICACIÓN DEL RESULTADO")
    print("=" * 60)
    if mejora_precision > 0:
        print(
            f"El KNN de contenido acierta {mejora_precision:.1%} más que recomendar simplemente\n"
            f"'lo más popular' a todo el mundo — es decir, SÍ está aprendiendo algo del perfil\n"
            f"de cada persona (sus categorías de interés), no solo repitiendo lo mismo para todos."
        )
    else:
        print(
            "El KNN de contenido no superó a la base de popularidad en esta corrida. Con pocos\n"
            "datos reales (todavía dependemos en gran parte de datos sintéticos), es esperable\n"
            "que la ventaja sea pequeña o inconsistente — hay que reevaluar cuando haya más\n"
            "valoraciones reales acumuladas (Etapa 12 en producción)."
        )
    print()

    # ---- Guardar el modelo entrenado ----
    os.makedirs(CARPETA_MODELOS, exist_ok=True)
    joblib.dump(
        {
            "modelo_knn": modelo_knn,
            "matriz_caracteristicas": matriz,
            "lugar_id_por_fila": lugar_id_por_fila,
            "columnas_caracteristicas": columnas,
            "precio_max": precio_max,
            "duracion_max": duracion_max,
            "version": "1.0",
            "fecha_entrenamiento": datetime.now(timezone.utc).isoformat(),
        },
        RUTA_MODELO,
    )
    print(f"Modelo guardado en: {RUTA_MODELO}")

    # ---- Registrar la versión en la base de datos (modelos_ml) ----
    db = SessionLocal()
    try:
        registro = ModeloML(
            nombre="Recomendador KNN de contenido",
            version="1.0",
            tipo="knn",
            metricas={"popularidad": metricas_popularidad, "knn_contenido": metricas_knn},
            ruta_archivo=os.path.abspath(RUTA_MODELO),
            fecha_entrenamiento=datetime.now(timezone.utc),
            # activo=False a propósito: todavía no reemplaza al recomendador
            # de reglas en producción — eso se decide en la Etapa 15.
            activo=False,
        )
        db.add(registro)
        db.commit()
        print(f"Registrado en modelos_ml con id={registro.id} (activo=False; se activa en la Etapa 15).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
