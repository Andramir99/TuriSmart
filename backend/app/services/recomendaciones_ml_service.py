"""Recomendador de Machine Learning real (Etapa 14-15): carga el modelo
KNN entrenado y lo usa para generar recomendaciones a partir del
HISTORIAL DE VALORACIONES de un usuario — a diferencia del recomendador
de reglas (Etapa 9), que usa preferencias declaradas en el momento.

Por eso conviven los dos: este endpoint solo funciona para alguien que
ya calificó al menos un lugar con 4-5 estrellas (si no, no hay perfil
que construir); para usuarios nuevos sigue siendo necesario
POST /recomendaciones (reglas).
"""

import threading

import joblib
from sqlalchemy.orm import Session

from app.models.modelos_ml import ModeloML
from app.models.recomendaciones import Recomendacion
from app.models.valoraciones import Valoracion
from app.services import lugares_service

PUNTUACION_MINIMA_PARA_PERFIL = 4

_bloqueo_carga_modelo = threading.Lock()
_cache_modelo: dict[str, dict] = {}


def _obtener_modelo_activo(db: Session) -> ModeloML | None:
    return (
        db.query(ModeloML)
        .filter(ModeloML.tipo == "knn", ModeloML.activo.is_(True))
        .order_by(ModeloML.fecha_entrenamiento.desc())
        .first()
    )


def _cargar_datos_modelo(ruta_archivo: str) -> dict:
    # Evita releer el archivo .joblib del disco en cada request — se
    # carga una vez por ruta y se reutiliza en memoria. El candado evita
    # que, con muchos usuarios concurrentes pidiendo recomendaciones por
    # primera vez (visto en la prueba de carga con 50 usuarios), varios
    # hilos entren a la vez antes de que el caché quede listo y cada uno
    # repita la carga del disco en paralelo, multiplicando el uso de CPU
    # justo en ese instante. Con el candado, solo el primer hilo carga de
    # verdad; los demás esperan y reciben el resultado ya cacheado.
    datos = _cache_modelo.get(ruta_archivo)
    if datos is not None:
        return datos
    with _bloqueo_carga_modelo:
        datos = _cache_modelo.get(ruta_archivo)
        if datos is None:
            datos = joblib.load(ruta_archivo)
            _cache_modelo[ruta_archivo] = datos
        return datos


def obtener_info_modelo_activo(db: Session) -> ModeloML | None:
    return _obtener_modelo_activo(db)


def generar_recomendaciones_ml(db: Session, usuario_id: int, k: int = 5) -> list[dict]:
    registro_modelo = _obtener_modelo_activo(db)
    if registro_modelo is None:
        raise ValueError(
            "Todavía no hay un modelo de Machine Learning activo. "
            "Usa POST /recomendaciones (recomendador por reglas) mientras tanto."
        )

    datos_modelo = _cargar_datos_modelo(registro_modelo.ruta_archivo)
    modelo_knn = datos_modelo["modelo_knn"]
    matriz = datos_modelo["matriz_caracteristicas"]
    lugar_id_por_fila = datos_modelo["lugar_id_por_fila"]

    valoraciones_usuario = (
        db.query(Valoracion)
        .filter(Valoracion.usuario_id == usuario_id, Valoracion.lugar_id.isnot(None))
        .all()
    )
    if not valoraciones_usuario:
        raise ValueError(
            "Todavía no calificaste ningún lugar. El modelo entrenado necesita al menos "
            "una valoración tuya para armar tu perfil — mientras tanto, usa "
            "POST /recomendaciones (recomendador por reglas)."
        )

    lugares_que_le_gustaron = [
        v.lugar_id for v in valoraciones_usuario if v.puntuacion >= PUNTUACION_MINIMA_PARA_PERFIL
    ]
    if not lugares_que_le_gustaron:
        raise ValueError(
            "Todavía no calificaste ningún lugar con 4 o 5 estrellas. El modelo entrenado "
            "arma tu perfil a partir de lo que SÍ te gustó — mientras tanto, usa "
            "POST /recomendaciones (recomendador por reglas)."
        )

    ya_valorados = {v.lugar_id for v in valoraciones_usuario}

    fila_por_lugar = {lugar_id: fila for fila, lugar_id in enumerate(lugar_id_por_fila)}
    filas_de_interes = [fila_por_lugar[lid] for lid in lugares_que_le_gustaron if lid in fila_por_lugar]
    if not filas_de_interes:
        raise ValueError("Los lugares que calificaste no están en el catálogo con el que se entrenó el modelo.")

    perfil_usuario = matriz[filas_de_interes].mean(axis=0, keepdims=True)
    distancias, vecinos = modelo_knn.kneighbors(perfil_usuario, n_neighbors=len(matriz))

    resultados = []
    for distancia, fila in zip(distancias[0], vecinos[0]):
        lugar_id = lugar_id_por_fila[fila]
        if lugar_id in ya_valorados:
            continue

        lugar = lugares_service.obtener_por_id(db, lugar_id)
        if lugar is None:
            continue

        # La distancia coseno del KNN va de 0 (idéntico) a ~2 (opuesto);
        # para lugares reales (características no negativas) rara vez
        # pasa de 1. La convertimos a una "puntuación" de afinidad 0-1,
        # más fácil de leer que una distancia.
        similitud = max(0.0, 1 - distancia)

        resultados.append(
            {
                "lugar": lugar,
                "puntuacion": round(float(similitud), 4),
                "motivo": (
                    f"El modelo entrenado (KNN, {registro_modelo.version}) identificó que "
                    f"{lugar.nombre} es similar a otros lugares que calificaste con "
                    f"{PUNTUACION_MINIMA_PARA_PERFIL}-5 estrellas."
                ),
            }
        )
        if len(resultados) == k:
            break

    for item in resultados:
        db.add(
            Recomendacion(
                usuario_id=usuario_id,
                lugar_id=item["lugar"].id,
                modelo_id=registro_modelo.id,
                puntuacion=item["puntuacion"],
                motivo=item["motivo"],
            )
        )
    db.commit()

    return resultados
