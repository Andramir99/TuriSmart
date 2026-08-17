"""Genera datos SINTÉTICOS (usuarios, encuestas, interacciones y
valoraciones) para poder entrenar y evaluar el modelo de recomendación
(Etapa 14) con volumen suficiente mientras se acumulan respuestas reales.

⚠️  IMPORTANTE PARA LA TESIS: estos datos son inventados con un
    generador aleatorio (semilla fija, para que sean reproducibles), NO
    son respuestas de personas reales. Cada fila queda marcada con
    es_sintetico = True en usuarios, encuestas, interacciones y
    valoraciones, para poder excluirlas de cualquier análisis que se
    presente como resultado real de la investigación.

Diseño: cada "persona sintética" es una cuenta de verdad (usuarios.es_sintetico
= True) con UNA encuesta que declara sus categorías de interés, y varias
interacciones/valoraciones DE ESA MISMA CUENTA. A propósito, sus
calificaciones están correlacionadas con lo que declaró le interesa
(alguien que dijo "cultura" califica mejor y visita más los lugares
culturales) — sin esa correlación, no habría ningún patrón real que un
modelo pudiera aprender, y evaluarlo no tendría sentido.

Ejecutar desde backend/, con el entorno virtual activado:
    python scripts/03_generar_datos_sinteticos.py [cantidad_de_personas]

Es idempotente: al empezar, BORRA cualquier dato sintético previo (todo
lo marcado es_sintetico=True) y lo vuelve a generar desde cero. Los
datos reales nunca se tocan.
"""

import os
import random
import sys
from datetime import datetime, timedelta, timezone

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.seguridad import hash_contrasena  # noqa: E402
from app.database.conexion import SessionLocal  # noqa: E402
from app.models.categorias import Categoria  # noqa: E402
from app.models.encuestas import Encuesta, RespuestaEncuesta  # noqa: E402
from app.models.interacciones import Interaccion  # noqa: E402
from app.models.lugares import Lugar  # noqa: E402
from app.models.usuarios import Usuario  # noqa: E402
from app.models.valoraciones import Valoracion  # noqa: E402

SEMILLA = 42
CANTIDAD_POR_DEFECTO = 150
CONTRASENA_DUMMY = "sintetico-no-usar-2026"  # ninguna cuenta sintética se usa para iniciar sesión

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
    None, None, None,
    "Muy buena experiencia, lo recomiendo.",
    "Estuvo bien, aunque esperaba un poco más.",
    "Excelente para ir en familia.",
    "El lugar es bonito pero estaba muy lleno.",
    "Vale la pena la entrada.",
]


def borrar_datos_sinteticos_previos(db) -> None:
    print("Borrando datos sintéticos previos (si había)...")
    db.query(Valoracion).filter(Valoracion.es_sintetico.is_(True)).delete()
    db.query(Interaccion).filter(Interaccion.es_sintetico.is_(True)).delete()
    # respuestas_encuesta se borra sola por el cascade="all, delete-orphan"
    # de Encuesta.respuestas al borrar la encuesta.
    db.query(Encuesta).filter(Encuesta.es_sintetico.is_(True)).delete()
    db.query(Usuario).filter(Usuario.es_sintetico.is_(True)).delete()
    db.commit()


def crear_persona_sintetica(db, indice: int, categorias: list[Categoria], lugares: list[Lugar], ahora) -> None:
    fecha = ahora - timedelta(days=random.randint(0, 180))

    usuario = Usuario(
        nombre=f"Persona Sintética {indice:03d}",
        correo=f"sintetico{indice:03d}@turismart.dev",
        contrasena_hash=hash_contrasena(CONTRASENA_DUMMY),
        es_sintetico=True,
    )
    db.add(usuario)
    db.flush()  # asigna usuario.id

    # ---- Encuesta: declara entre 1 y 3 categorías de interés ----
    interes = random.sample([c.slug for c in categorias], k=random.randint(1, 3))
    encuesta = Encuesta(
        usuario_id=usuario.id,
        consentimiento_datos=True,
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

    # ---- Interacciones y valoraciones de ESTA MISMA persona ----
    # 70% de los lugares que "visita" son de sus categorías declaradas
    # (así el modelo tiene un patrón real que aprender); el 30% restante
    # es exploración fuera de sus intereses, como pasa en la vida real.
    lugares_de_interes = [lugar for lugar in lugares if lugar.categoria.slug in interes]
    lugares_fuera_interes = [lugar for lugar in lugares if lugar.categoria.slug not in interes]

    cantidad_lugares = random.randint(3, 7)
    cantidad_de_interes = round(cantidad_lugares * 0.7)
    seleccion = random.sample(lugares_de_interes, k=min(cantidad_de_interes, len(lugares_de_interes)))
    seleccion += random.sample(
        lugares_fuera_interes, k=min(cantidad_lugares - len(seleccion), len(lugares_fuera_interes))
    )

    for lugar in seleccion:
        coincide = lugar.categoria.slug in interes

        tipo = random.choices(
            ["vista", "clic", "recomendacion_aceptada", "recomendacion_rechazada"],
            weights=[35, 25, 30, 10] if coincide else [40, 20, 10, 30],
        )[0]
        interaccion = Interaccion(usuario_id=usuario.id, lugar_id=lugar.id, tipo_interaccion=tipo, es_sintetico=True)
        interaccion.fecha = fecha + timedelta(hours=random.randint(0, 72))
        db.add(interaccion)

        if random.random() < 0.65:
            # Sesgo hacia puntuaciones altas cuando coincide con lo que
            # declaró que le interesa; más disperso (incluye bajas)
            # cuando no coincide. Esta diferencia ES la señal que el
            # recomendador de contenido (Etapa 14) tiene que aprender.
            if coincide:
                puntuacion = random.choices([1, 2, 3, 4, 5], weights=[1, 2, 12, 35, 50])[0]
            else:
                puntuacion = random.choices([1, 2, 3, 4, 5], weights=[10, 20, 35, 25, 10])[0]

            valoracion = Valoracion(
                usuario_id=usuario.id,
                lugar_id=lugar.id,
                puntuacion=puntuacion,
                recomendacion_util=coincide if random.random() < 0.8 else not coincide,
                estado_visita=random.choice(["visitado", "visitado", "descartado", "pendiente"]),
                comentario=random.choice(COMENTARIOS_POSIBLES),
                es_sintetico=True,
            )
            valoracion.fecha = fecha + timedelta(hours=random.randint(0, 72))
            db.add(valoracion)


def main():
    cantidad = int(sys.argv[1]) if len(sys.argv) > 1 else CANTIDAD_POR_DEFECTO
    random.seed(SEMILLA)

    db = SessionLocal()
    try:
        categorias = db.query(Categoria).all()
        lugares = db.query(Lugar).filter(Lugar.activo.is_(True)).all()
        for lugar in lugares:
            _ = lugar.categoria  # fuerza a cargar la relación antes del loop

        if not categorias or not lugares:
            print("Faltan categorías o lugares en la base de datos.")
            print("Corre primero: python scripts/02_sembrar_datos_iniciales.py")
            return

        borrar_datos_sinteticos_previos(db)

        print(f"Generando {cantidad} personas sintéticas (usuario + encuesta + interacciones + valoraciones)...")
        ahora = datetime.now(timezone.utc)
        for indice in range(1, cantidad + 1):
            crear_persona_sintetica(db, indice, categorias, lugares, ahora)
            if indice % 25 == 0:
                db.commit()
                print(f"  ...{indice}/{cantidad}")
        db.commit()

        print("Listo. Todo quedó marcado con es_sintetico = True.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
