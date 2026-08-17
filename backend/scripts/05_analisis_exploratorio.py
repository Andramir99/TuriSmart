"""Etapa 13 — Análisis exploratorio (EDA) sobre el dataset ya preparado
por scripts/04_preparar_dataset.py.

Lee los CSV de data/processed/, imprime estadísticas descriptivas en la
consola, y guarda un puñado de gráficos en data/processed/eda/. Es el
primer vistazo a los datos antes de decidir cómo limpiarlos/codificarlos
y entrenar el modelo (Etapa 14) — sirve para notar cosas como "casi
nadie eligió tal categoría" o "las valoraciones están muy sesgadas hacia
5 estrellas", que después importan para elegir el algoritmo y las
métricas correctas.

⚠️  Si el dataset se preparó con --incluir-sinteticos, estos números
    NO describen turistas reales — son solo para verificar que el
    pipeline (consulta → limpieza → gráfico) funciona de punta a punta.

Ejecutar desde backend/, con el entorno virtual activado:
    python scripts/05_analisis_exploratorio.py
"""

import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

import matplotlib

matplotlib.use("Agg")  # sin esto, matplotlib intenta abrir una ventana
import matplotlib.pyplot as plt
import pandas as pd

CARPETA_DATOS = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")
CARPETA_GRAFICOS = os.path.join(CARPETA_DATOS, "eda")

plt.rcParams["figure.autolayout"] = True


def cargar_csv(nombre: str) -> pd.DataFrame:
    ruta = os.path.join(CARPETA_DATOS, nombre)
    if not os.path.exists(ruta):
        print(f"No existe {ruta}.")
        print("Corre primero: python scripts/04_preparar_dataset.py --incluir-sinteticos")
        sys.exit(1)
    return pd.read_csv(ruta)


def analizar_encuestas(encuestas: pd.DataFrame) -> None:
    print("=" * 60)
    print("ENCUESTAS / PERFILES DE VIAJERO")
    print("=" * 60)
    print(f"Total: {len(encuestas)}  (sintéticas: {encuestas['es_sintetico'].sum()})")
    print()

    print("-- Distribución de presupuesto --")
    print(encuestas["presupuesto"].value_counts())
    print()

    print("-- Distribución de duración del viaje (días) --")
    print(encuestas["duracion_dias"].describe())
    print()

    # "categorias_interes" viene como texto separado por comas
    # ("cultural,natural"); para contar cuántas veces se eligió cada
    # categoría hay que "explotar" esa columna en una fila por categoría.
    categorias_explotadas = (
        encuestas["categorias_interes"].dropna().str.split(",").explode().str.strip()
    )
    print("-- Categorías de interés más elegidas --")
    print(categorias_explotadas.value_counts())
    print()

    fig, ejes = plt.subplots(1, 2, figsize=(11, 4))
    encuestas["presupuesto"].value_counts().plot(kind="bar", ax=ejes[0], color="#c1443c")
    ejes[0].set_title("Presupuesto declarado")
    ejes[0].set_ylabel("Encuestas")

    categorias_explotadas.value_counts().plot(kind="barh", ax=ejes[1], color="#3355cc")
    ejes[1].set_title("Categorías de interés")
    ejes[1].set_xlabel("Veces elegida")

    guardar_grafico(fig, "encuestas_presupuesto_categorias.png")


def analizar_eventos(eventos: pd.DataFrame) -> None:
    print("=" * 60)
    print("INTERACCIONES Y VALORACIONES")
    print("=" * 60)
    print(f"Total: {len(eventos)}  (sintéticas: {eventos['es_sintetico'].sum()})")
    print()

    print("-- Tipos de evento --")
    print(eventos["tipo_evento"].value_counts())
    print()

    valoraciones = eventos[eventos["tipo_evento"] == "valoracion"]
    if not valoraciones.empty:
        print("-- Distribución de puntuación (1-5 estrellas) --")
        print(valoraciones["puntuacion"].value_counts().sort_index())
        print(f"Promedio general: {valoraciones['puntuacion'].mean():.2f}")
        print()

        print("-- Puntuación promedio por categoría de lugar --")
        print(valoraciones.groupby("categoria_slug")["puntuacion"].mean().sort_values(ascending=False))
        print()

        fig, ejes = plt.subplots(1, 2, figsize=(11, 4))
        valoraciones["puntuacion"].value_counts().sort_index().plot(
            kind="bar", ax=ejes[0], color="#d9822b"
        )
        ejes[0].set_title("Distribución de puntuaciones")
        ejes[0].set_xlabel("Estrellas")
        ejes[0].set_ylabel("Cantidad")

        valoraciones.groupby("categoria_slug")["puntuacion"].mean().sort_values().plot(
            kind="barh", ax=ejes[1], color="#2e7d32"
        )
        ejes[1].set_title("Puntuación promedio por categoría")
        ejes[1].set_xlim(0, 5)

        guardar_grafico(fig, "valoraciones_distribucion.png")

    print("-- Interacciones (no-valoración) por tipo y categoría --")
    interacciones = eventos[eventos["tipo_evento"] != "valoracion"]
    if not interacciones.empty:
        tabla = pd.crosstab(interacciones["categoria_slug"], interacciones["tipo_evento"])
        print(tabla)
        print()

        fig, eje = plt.subplots(figsize=(8, 4))
        tabla.plot(kind="bar", stacked=True, ax=eje)
        eje.set_title("Interacciones por categoría")
        eje.set_ylabel("Cantidad")
        guardar_grafico(fig, "interacciones_por_categoria.png")


def analizar_recomendaciones_aceptadas(eventos: pd.DataFrame) -> None:
    print("=" * 60)
    print("¿SE ACEPTAN LAS RECOMENDACIONES? (recomendador de la Etapa 9)")
    print("=" * 60)
    recomendaciones = eventos[
        eventos["tipo_evento"].isin(["recomendacion_aceptada", "recomendacion_rechazada"])
    ]
    if recomendaciones.empty:
        print("Todavía no hay reacciones a recomendaciones registradas.")
        return

    conteo = recomendaciones["tipo_evento"].value_counts()
    total = conteo.sum()
    aceptadas = conteo.get("recomendacion_aceptada", 0)
    print(f"Aceptadas: {aceptadas}/{total} ({aceptadas / total:.1%})")
    print()


def guardar_grafico(fig, nombre_archivo: str) -> None:
    os.makedirs(CARPETA_GRAFICOS, exist_ok=True)
    ruta = os.path.join(CARPETA_GRAFICOS, nombre_archivo)
    fig.savefig(ruta, dpi=120)
    plt.close(fig)
    print(f"[gráfico guardado] {ruta}")
    print()


def main():
    encuestas = cargar_csv("encuestas.csv")
    eventos = cargar_csv("interacciones_valoraciones.csv")

    if encuestas.empty and eventos.empty:
        print("El dataset está vacío. Corre scripts/04_preparar_dataset.py primero")
        print("(con --incluir-sinteticos si todavía no hay suficientes datos reales).")
        return

    if not encuestas.empty:
        analizar_encuestas(encuestas)
    if not eventos.empty:
        analizar_eventos(eventos)
        analizar_recomendaciones_aceptadas(eventos)

    print("Listo. Revisa las imágenes en:", CARPETA_GRAFICOS)


if __name__ == "__main__":
    main()
