"""Etapa 13 — Prepara el dataset anonimizado a partir de lo acumulado en
PostgreSQL (encuestas, interacciones, valoraciones) y lo exporta a CSV
dentro de data/processed/, listo para el análisis exploratorio
(scripts/05_analisis_exploratorio.py) y, más adelante, para entrenar el
modelo (Etapa 14).

Anonimización: ningún archivo exportado contiene el id real de un
usuario, su nombre ni su correo. En vez de eso, a cada usuario se le
asigna un "usuario_hash" — el resultado de aplicarle SHA-256 a su id
real más una sal fija (SAL_ANONIMIZACION). Esto permite seguir
relacionando las respuestas de UNA MISMA persona entre sí (algo que el
modelo necesita: "este perfil de viajero calificó así estos lugares"),
sin exponer de quién se trata. Las filas de usuarios anónimos (sin
sesión iniciada) simplemente no tienen forma de conectarse entre ellas
y se excluyen del dataset de entrenamiento por esa razón (se explica
más abajo, en `preparar_dataset_entrenamiento`).

Salidas (en data/processed/):
  - encuestas.csv                 Un perfil de viajero por fila.
  - interacciones_valoraciones.csv Cada valoración/interacción, con las
                                    características del lugar.
  - dataset_entrenamiento.csv      Perfil de viajero + lo que calificó,
                                    unidos por usuario_hash — SOLO para
                                    quienes tenían sesión iniciada.

Ejecutar desde backend/, con el entorno virtual activado:
    python scripts/04_preparar_dataset.py [--incluir-sinteticos]

Por defecto, el dataset usa solo datos reales. Con --incluir-sinteticos
se agregan también las filas generadas por
scripts/03_generar_datos_sinteticos.py (marcadas es_sintetico=True) —
útil para poder mostrar el pipeline completo mientras se acumulan
suficientes respuestas reales, pero NUNCA deben presentarse como
resultados reales de la investigación.
"""

import hashlib
import os
import sys

# La consola de Windows (PowerShell/cmd) por defecto no usa UTF-8, así
# que print() con emojis o algunos caracteres especiales revienta con
# UnicodeEncodeError. Forzamos UTF-8 en la salida para que este script
# corra igual en Windows, Mac o Linux.
sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database.conexion import engine  # noqa: E402

# No es un secreto de seguridad (los ids de usuario no son información
# sensible por sí solos) — es solo para que el mismo usuario_id siempre
# produzca el mismo hash entre corridas del script, y así se puedan
# agrupar sus respuestas. Ver el docstring de arriba.
SAL_ANONIMIZACION = "turismart-lima-tesis-2026"

CARPETA_SALIDA = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")


def anonimizar_usuario_id(usuario_id) -> str | None:
    if usuario_id is None or pd.isna(usuario_id):
        return None
    texto = f"{SAL_ANONIMIZACION}:{int(usuario_id)}"
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]


def cargar_encuestas(incluir_sinteticos: bool) -> pd.DataFrame:
    condicion = "" if incluir_sinteticos else "WHERE e.es_sintetico = false"
    consulta = f"""
        SELECT e.id AS encuesta_id, e.usuario_id, e.es_sintetico,
               e.fecha_creacion, r.pregunta, r.respuesta
        FROM encuestas e
        JOIN respuestas_encuesta r ON r.encuesta_id = e.id
        {condicion}
    """
    largo = pd.read_sql(consulta, engine)
    if largo.empty:
        return largo

    # Las respuestas vienen en formato "largo" (una fila por pregunta,
    # ver el modelo RespuestaEncuesta): las "pivoteamos" a formato ancho
    # (una fila por encuesta, una columna por pregunta) porque así es
    # como cualquier modelo de ML espera recibir las características.
    #
    # Se pivotea usando SOLO "encuesta_id" como índice (no las 4 columnas
    # de metadatos juntas): pivot_table arma el PRODUCTO CARTESIANO de
    # los valores únicos de cada columna del índice cuando hay más de
    # una — con usuario_id casi siempre NaN (encuestas anónimas), eso
    # generaba decenas de miles de filas fantasma. Los metadatos
    # (usuario_id, es_sintetico, fecha_creacion) se pegan aparte con un
    # merge normal, que no tiene ese problema.
    metadatos = largo[["encuesta_id", "usuario_id", "es_sintetico", "fecha_creacion"]].drop_duplicates(
        subset=["encuesta_id"]
    )
    respuestas_pivoteadas = largo.pivot_table(
        index="encuesta_id", columns="pregunta", values="respuesta", aggfunc="first"
    ).reset_index()

    ancho = metadatos.merge(respuestas_pivoteadas, on="encuesta_id", how="left")
    ancho["usuario_hash"] = ancho["usuario_id"].apply(anonimizar_usuario_id)
    ancho = ancho.drop(columns=["usuario_id"])
    return ancho


def cargar_interacciones_y_valoraciones(incluir_sinteticos: bool) -> pd.DataFrame:
    condicion_v = "" if incluir_sinteticos else "AND v.es_sintetico = false"
    valoraciones = pd.read_sql(
        f"""
        SELECT v.usuario_id, v.lugar_id, v.itinerario_id, v.puntuacion,
               v.recomendacion_util, v.estado_visita, v.comentario,
               v.es_sintetico, v.fecha,
               l.categoria_id, c.slug AS categoria_slug, l.distrito,
               l.precio, l.accesible_movilidad_reducida
        FROM valoraciones v
        LEFT JOIN lugares l ON l.id = v.lugar_id
        LEFT JOIN categorias c ON c.id = l.categoria_id
        WHERE v.lugar_id IS NOT NULL {condicion_v}
        """,
        engine,
    )

    condicion_i = "" if incluir_sinteticos else "AND i.es_sintetico = false"
    interacciones = pd.read_sql(
        f"""
        SELECT i.usuario_id, i.lugar_id, i.itinerario_id, i.tipo_interaccion,
               i.es_sintetico, i.fecha,
               l.categoria_id, c.slug AS categoria_slug, l.distrito,
               l.precio, l.accesible_movilidad_reducida
        FROM interacciones i
        LEFT JOIN lugares l ON l.id = i.lugar_id
        LEFT JOIN categorias c ON c.id = l.categoria_id
        WHERE i.lugar_id IS NOT NULL {condicion_i}
        """,
        engine,
    )

    valoraciones["tipo_evento"] = "valoracion"
    interacciones["tipo_evento"] = interacciones["tipo_interaccion"]

    combinado = pd.concat([valoraciones, interacciones], ignore_index=True)
    if combinado.empty:
        return combinado

    combinado["usuario_hash"] = combinado["usuario_id"].apply(anonimizar_usuario_id)
    combinado = combinado.drop(columns=["usuario_id"])
    return combinado


def preparar_dataset_entrenamiento(encuestas: pd.DataFrame, eventos: pd.DataFrame) -> pd.DataFrame:
    """Une el perfil declarado (encuesta) con lo que esa MISMA persona
    calificó, usando usuario_hash como llave. Solo es posible para
    usuarios con sesión iniciada — las respuestas anónimas (usuario_hash
    vacío) no tienen forma de conectarse con nada más, así que quedan
    fuera de este archivo (aunque sí aparecen en los otros dos CSV).
    """
    if encuestas.empty or eventos.empty:
        return pd.DataFrame()

    encuestas_con_usuario = encuestas.dropna(subset=["usuario_hash"])
    eventos_con_usuario = eventos.dropna(subset=["usuario_hash"])

    return encuestas_con_usuario.merge(eventos_con_usuario, on="usuario_hash", how="inner")


def main():
    incluir_sinteticos = "--incluir-sinteticos" in sys.argv
    os.makedirs(CARPETA_SALIDA, exist_ok=True)

    print(f"Preparando dataset ({'con' if incluir_sinteticos else 'sin'} datos sintéticos)...")

    encuestas = cargar_encuestas(incluir_sinteticos)
    eventos = cargar_interacciones_y_valoraciones(incluir_sinteticos)
    entrenamiento = preparar_dataset_entrenamiento(encuestas, eventos)

    ruta_encuestas = os.path.join(CARPETA_SALIDA, "encuestas.csv")
    ruta_eventos = os.path.join(CARPETA_SALIDA, "interacciones_valoraciones.csv")
    ruta_entrenamiento = os.path.join(CARPETA_SALIDA, "dataset_entrenamiento.csv")

    encuestas.to_csv(ruta_encuestas, index=False, encoding="utf-8")
    eventos.to_csv(ruta_eventos, index=False, encoding="utf-8")
    entrenamiento.to_csv(ruta_entrenamiento, index=False, encoding="utf-8")

    print(f"  {ruta_encuestas}  ({len(encuestas)} perfiles de viajero)")
    print(f"  {ruta_eventos}  ({len(eventos)} interacciones/valoraciones)")
    print(f"  {ruta_entrenamiento}  ({len(entrenamiento)} filas unidas, solo usuarios con cuenta)")

    if not incluir_sinteticos and len(encuestas) < 30:
        print()
        print("⚠️  Muy pocas encuestas reales todavía. Para probar el pipeline")
        print("    completo, corre con --incluir-sinteticos (recuerda que esas")
        print("    filas NO son datos reales de la investigación).")


if __name__ == "__main__":
    main()
