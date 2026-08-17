"""Funciones geográficas puras, compartidas por el recomendador (Etapa 9)
y el cálculo de distancia estimada de un itinerario (Etapa 10).
"""

from math import asin, cos, radians, sin, sqrt


def distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia en línea recta entre dos coordenadas (fórmula de
    Haversine). No es la distancia real por calles — para eso haría falta
    un servicio de rutas, que no es parte de esta etapa.
    """
    radio_tierra_km = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return radio_tierra_km * 2 * asin(sqrt(a))
