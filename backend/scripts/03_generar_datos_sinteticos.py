"""Genera datos SINTÉTICOS (encuestas, interacciones y valoraciones) para
poder ejecutar y mostrar el pipeline de datos (Etapa 13) y, más adelante,
entrenar el modelo (Etapa 14) con volumen suficiente.

⚠️  IMPORTANTE PARA LA TESIS: estos datos son inventados con un
    generador aleatorio (semilla fija, para que sean reproducibles), NO
    son respuestas reales de personas. Cada fila queda marcada con
    es_sintetico = True (columna agregada en esta etapa) precisamente
    para que scripts/04_preparar_dataset.py pueda excluirlas si algún
    día hay que reportar resultados reales, o incluirlas explícitamente
    solo para demostrar que la integración técnica funciona.

Ejecutar desde backend/, con el entorno virtual activado:
    python scripts/03_generar_datos_sinteticos.py [cantidad_de_sesiones]

Es seguro correrlo varias veces: cada corrida agrega más filas sintéticas
nuevas, no borra ni duplica las que ya había con el mismo criterio raro
de "duplicado" (no hay una clave natural para deduplicar una encuesta).
Si quieres empezar de cero, borra antes las filas con es_sintetico=True.
"""

import os
import random
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database.conexion import SessionLocal  # noqa: E402
from app.models.categorias import Categoria  # noqa: E402
from app.models.encuestas import Encuesta, RespuestaEncuesta  # noqa: E402
from app.models.interacciones import Interaccion  # noqa: E402
from app.models.lugares import Lugar  # noqa: E402
from app.models.valoraciones import Valoracion  # noqa: E402

SEMILLA = 42  # fija: correr el script siempre genera los mismos datos
CANTIDAD_POR_DEFECTO = 150

DISTRITOS = [
    "Cercado de Lima", "Barranco", "Miraflores", "San Isidro", "San Borja",
    "Surco", "La Molina", "Pueblo Libre", "Jesús María", "Lince",
    "San Miguel", "Magdalena del Mar", "Chorrillos", "Rímac",
]
PRESUPUESTOS = ["economico", "moderado", "premium"]
GRUPOS = ["solo", "pareja", "familia", "amigos"]
HORARIOS = ["manana", "tarde", "noche", "cualquiera"]
IDIOMAS = ["es", "en", "pt"]
COMENTARIOS_POSIBLES = [
    None, None, None,  # la mayoría de valoraciones no traen comentario
    "Muy buena experiencia, lo recomiendo.",
    "Estuvo bien, aunque esperaba un poco más.",
    "Excelente para ir en familia.",
    "El lugar es bonito pero estaba muy lleno.",
    "Vale la pena la entrada.",
]


def generar_encuestas_sinteticas(db, categorias: list[Categoria], cantidad: int) -> list[Encuesta]:
    encuestas = []
    ahora = datetime.now(timezone.utc)

    for _ in range(cantidad):
        interes = random.sample([c.slug for c in categorias], k=random.randint(1, 3))
        fecha = ahora - timedelta(days=random.randint(0, 180))

        encuesta = Encuesta(
            usuario_id=None,  # las sintéticas son anónimas a propósito
            consentimiento_datos=True,
            # version_encuesta es VARCHAR(10) en la base de datos — "sint-1.0"
            # (8 caracteres) es el máximo que cabe describiendo que es sintética.
            version_encuesta="sint-1.0",
            es_sintetico=True,
        )
        encuesta.fecha_creacion = fecha
        db.add(encuesta)
        db.flush()

        respuestas = {
            "categorias_interes": ",".join(interes),
            "duracion_dias": str(random.randint(1, 7)),
            "presupuesto": random.choice(PRESUPUESTOS),
            "tipo_compania": random.choice(GRUPOS),
            "distrito_partida": random.choice(DISTRITOS),
            "distancia_maxima_km": str(random.randint(3, 25)),
            "horario_preferido": random.choice(HORARIOS),
            "movilidad_reducida": random.choice(["true", "false", "false", "false"]),
            "idioma_preferido": random.choice(IDIOMAS),
        }
        for pregunta, respuesta in respuestas.items():
            db.add(RespuestaEncuesta(encuesta_id=encuesta.id, pregunta=pregunta, respuesta=respuesta))

        encuestas.append(encuesta)

    db.commit()
    return encuestas


def generar_interacciones_y_valoraciones_sinteticas(db, lugares: list[Lugar], cantidad_encuestas: int) -> None:
    ahora = datetime.now(timezone.utc)
    # Cada "sesión sintética" (que ya generó una encuesta) también ve,
    # califica o descarta unos pocos lugares — simula el comportamiento
    # de un usuario real usando la app después de responder la encuesta.
    for _ in range(cantidad_encuestas):
        lugares_de_la_sesion = random.sample(lugares, k=random.randint(2, 5))
        fecha = ahora - timedelta(days=random.randint(0, 180))

        for lugar in lugares_de_la_sesion:
            tipo = random.choices(
                ["vista", "clic", "recomendacion_aceptada", "recomendacion_rechazada"],
                weights=[40, 25, 20, 15],
            )[0]
            interaccion = Interaccion(
                usuario_id=None,
                lugar_id=lugar.id,
                tipo_interaccion=tipo,
                es_sintetico=True,
            )
            interaccion.fecha = fecha
            db.add(interaccion)

            # No todas las interacciones terminan en una valoración (en
            # la vida real, mucha gente ve un lugar y nunca lo califica).
            if random.random() < 0.6:
                # Sesgo hacia puntuaciones altas (3-5), como suele pasar
                # con valoraciones reales de plataformas de turismo.
                puntuacion = random.choices([1, 2, 3, 4, 5], weights=[3, 5, 20, 35, 37])[0]
                valoracion = Valoracion(
                    usuario_id=None,
                    lugar_id=lugar.id,
                    puntuacion=puntuacion,
                    recomendacion_util=random.choice([True, True, False]),
                    estado_visita=random.choice(["visitado", "visitado", "descartado", "pendiente"]),
                    comentario=random.choice(COMENTARIOS_POSIBLES),
                    es_sintetico=True,
                )
                valoracion.fecha = fecha
                db.add(valoracion)

    db.commit()


def main():
    cantidad = int(sys.argv[1]) if len(sys.argv) > 1 else CANTIDAD_POR_DEFECTO
    random.seed(SEMILLA)

    db = SessionLocal()
    try:
        categorias = db.query(Categoria).all()
        lugares = db.query(Lugar).filter(Lugar.activo.is_(True)).all()

        if not categorias or not lugares:
            print("Faltan categorías o lugares en la base de datos.")
            print("Corre primero: python scripts/02_sembrar_datos_iniciales.py")
            return

        print(f"Generando {cantidad} encuestas sintéticas...")
        generar_encuestas_sinteticas(db, categorias, cantidad)

        print("Generando interacciones y valoraciones sintéticas...")
        generar_interacciones_y_valoraciones_sinteticas(db, lugares, cantidad)

        print("Listo. Todas las filas quedaron marcadas con es_sintetico = True.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
