"""Perfil dinámico de preferencias del usuario (Etapa 16).

A diferencia del recomendador por reglas (Etapa 9, que usa lo que el
usuario declaró en el formulario) o el KNN offline (Etapa 14, que solo
mira valoraciones >= 4), este perfil se recalcula a partir de TODA la
interacción real del usuario dentro de la plataforma: búsquedas, filtros,
clics, tiempo revisando un lugar, "me gusta", itinerarios armados,
lugares visitados y reacciones a recomendaciones previas.

No se guarda como tabla aparte: se recalcula al vuelo a partir de
"interacciones" y "valoraciones" cada vez que se piden recomendaciones,
así siempre refleja el comportamiento más reciente sin necesitar un job
de actualización periódica. Con el volumen de datos de un prototipo esto
es rápido; si el catálogo o la base de usuarios creciera mucho, el mismo
resultado podría cachearse por usuario con una expiración corta.
"""

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session, joinedload

from app.ml.pesos_interacciones import (
    PESOS_INTERACCION,
    PUNTUACION_MAXIMA_COMO_RECHAZO,
    PUNTUACION_MINIMA_COMO_ME_GUSTA,
    UMBRAL_TIEMPO_RELEVANTE_SEGUNDOS,
)
from app.models.interacciones import Interaccion
from app.models.lugares import Lugar
from app.models.valoraciones import Valoracion

# Búsquedas/filtros de más de 90 días no deberían pesar igual que los de
# esta semana — el interés de un usuario cambia con el tiempo. No es una
# fórmula de decaimiento exponencial (fuera de alcance del prototipo),
# es una ventana simple: cuenta completo lo reciente, cuenta la mitad lo
# anterior a eso.
VENTANA_RECIENTE_DIAS = 30
FACTOR_FUERA_DE_VENTANA = 0.5


class PerfilCategoria:
    __slots__ = ("puntaje", "senales")

    def __init__(self) -> None:
        self.puntaje: float = 0.0
        # tipo_interaccion -> peso acumulado, para saber cuál dominó y
        # elegir una explicación honesta (ver FRASE_POR_SENAL).
        self.senales: dict[str, float] = defaultdict(float)

    def sumar(self, tipo: str, peso: float) -> None:
        self.puntaje += peso
        if peso > 0:
            self.senales[tipo] += peso

    def senal_dominante(self) -> str | None:
        if not self.senales:
            return None
        return max(self.senales, key=self.senales.get)


def _factor_recencia(fecha: datetime) -> float:
    if fecha.tzinfo is None:
        fecha = fecha.replace(tzinfo=timezone.utc)
    limite = datetime.now(timezone.utc) - timedelta(days=VENTANA_RECIENTE_DIAS)
    return 1.0 if fecha >= limite else FACTOR_FUERA_DE_VENTANA


def calcular_perfil(db: Session, usuario_id: int) -> dict[str, PerfilCategoria]:
    """Devuelve {categoria_slug: PerfilCategoria}, normalizado entre 0 y 1
    por categoría (0 = sin señal de interés, 1 = la categoría con más
    interés relativo del usuario). Un dict vacío significa "usuario sin
    historial suficiente" — quien llama debe usar cold start en ese caso.
    """
    perfil: dict[str, PerfilCategoria] = defaultdict(PerfilCategoria)

    interacciones = (
        db.query(Interaccion)
        .options(joinedload(Interaccion.lugar).joinedload(Lugar.categoria))
        .filter(Interaccion.usuario_id == usuario_id)
        .all()
    )
    for ia in interacciones:
        peso_base = PESOS_INTERACCION.get(ia.tipo_interaccion)
        if not peso_base:
            continue

        if ia.tipo_interaccion == "tiempo_visualizacion":
            segundos = (ia.metadatos or {}).get("segundos", 0)
            if segundos < UMBRAL_TIEMPO_RELEVANTE_SEGUNDOS:
                continue

        # búsqueda/filtro no siempre tienen lugar_id (el usuario buscó
        # "museos" sin hacer clic en ninguno todavía): la categoría viene
        # en metadatos si el frontend la mandó, y si no, se descarta la
        # señal para el perfil (igual queda registrada para análisis).
        categoria_slug = None
        if ia.lugar is not None:
            categoria_slug = ia.lugar.categoria.slug
        elif ia.metadatos:
            categoria_slug = ia.metadatos.get("categoria")
        if not categoria_slug:
            continue

        peso = peso_base * _factor_recencia(ia.fecha)
        perfil[categoria_slug].sumar(ia.tipo_interaccion, peso)

    valoraciones = (
        db.query(Valoracion)
        .options(joinedload(Valoracion.lugar).joinedload(Lugar.categoria))
        .filter(Valoracion.usuario_id == usuario_id, Valoracion.lugar_id.isnot(None))
        .all()
    )
    for val in valoraciones:
        if val.lugar is None:
            continue
        categoria_slug = val.lugar.categoria.slug
        if val.puntuacion >= PUNTUACION_MINIMA_COMO_ME_GUSTA:
            peso = PESOS_INTERACCION["me_gusta"] * _factor_recencia(val.fecha)
            perfil[categoria_slug].sumar("valoracion", peso)
        elif val.puntuacion <= PUNTUACION_MAXIMA_COMO_RECHAZO:
            peso = -1.0 * _factor_recencia(val.fecha)
            perfil[categoria_slug].sumar("valoracion", peso)

    if not perfil:
        return {}

    maximo = max(p.puntaje for p in perfil.values())
    if maximo <= 0:
        return {}
    for p in perfil.values():
        p.puntaje = max(0.0, round(p.puntaje / maximo, 4))

    return dict(perfil)
