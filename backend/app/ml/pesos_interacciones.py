"""Pesos de cada tipo de interacción, usados para construir el perfil
dinámico de preferencias del usuario (recomendador híbrido, Etapa 16).

Centralizados en un solo diccionario para que se puedan ajustar sin tocar
el servicio que los usa, y para poder reutilizarlos como feature al
entrenar un modelo más adelante.
"""

PESOS_INTERACCION: dict[str, float] = {
    "vista": 0.1,
    "clic": 0.5,
    "recomendacion_abierta": 0.5,
    "recomendacion_aceptada": 2.0,
    "recomendacion_rechazada": -1.0,
    "recomendacion_mostrada": 0.0,  # no suma al perfil; solo sirve para medir tasa de ignoradas
    "recomendacion_ignorada": -0.2,
    "tiempo_visualizacion": 1.0,  # solo cuenta si metadatos.segundos >= UMBRAL_TIEMPO_RELEVANTE_SEGUNDOS
    "busqueda": 1.0,
    "busqueda_repetida": 1.5,  # 2da+ búsqueda de la misma categoría en la ventana reciente
    "filtro": 1.0,
    "me_gusta": 3.0,
    "quitar_me_gusta": -2.0,
    "agregado_itinerario": 4.0,
    "eliminar_itinerario": -1.0,
    "compartir": 2.0,
    "marcado_visitado": 2.0,
}

# Una "vista" muy corta (alguien que entra y sale) pesa menos que quedarse
# revisando fotos y detalles. Por debajo de este umbral no se registra
# tiempo_visualizacion como señal de interés.
UMBRAL_TIEMPO_RELEVANTE_SEGUNDOS = 20

# Valoración explícita (estrellas) con la que un lugar se trata como si el
# usuario le hubiera dado "me gusta" implícitamente para el perfil.
PUNTUACION_MINIMA_COMO_ME_GUSTA = 4
PUNTUACION_MAXIMA_COMO_RECHAZO = 2

# Motivo legible por tipo de señal dominante (Etapa 16, punto 9 del pedido:
# explicar sin exponer el cálculo técnico ni datos privados).
FRASE_POR_SENAL = {
    "busqueda": "Relacionado con tus búsquedas recientes.",
    "busqueda_repetida": "Recomendado porque últimamente estás explorando lugares de {categoria}.",
    "filtro": "Coincide con los filtros que sueles usar.",
    "clic": "Porque has estado revisando lugares de {categoria}.",
    "tiempo_visualizacion": "Porque te detuviste a revisar lugares de {categoria}.",
    "me_gusta": "Similar a otros lugares que marcaste con Me gusta.",
    "agregado_itinerario": "Creemos que podría gustarte porque agregaste lugares de {categoria} a tu itinerario.",
    "marcado_visitado": "Parecido a lugares de {categoria} que ya visitaste y te gustaron.",
    "compartir": "Similar a lugares de {categoria} que compartiste.",
    "valoracion": "Porque calificaste bien otros lugares de {categoria}.",
}
