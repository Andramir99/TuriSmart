"""Siembra (seed) de datos iniciales: categorías + lugares.

Ejecutar UNA vez, con el entorno virtual activado, desde la carpeta backend/:
    python scripts/02_sembrar_datos_iniciales.py

Es idempotente: si una categoría o un lugar con el mismo nombre ya existe,
el script lo salta en vez de duplicarlo, así que se puede volver a correr
sin miedo (por ejemplo, después de agregar más lugares a la lista de abajo).

Los precios, horarios y duraciones son aproximados — sirven para probar
el catálogo y el recomendador (Etapas 9 y siguientes), no son datos
turísticos oficiales verificados.
"""

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from geoalchemy2.elements import WKTElement  # noqa: E402

from app.database.conexion import SessionLocal  # noqa: E402
from app.models import Categoria, Lugar  # noqa: E402

CATEGORIAS = [
    {"slug": "cultural", "nombre": "Cultura & Historia", "descripcion": "Museos, plazas y arquitectura colonial", "icono": "bi-bank"},
    {"slug": "natural", "nombre": "Naturaleza", "descripcion": "Lomas, parques y costa verde", "icono": "bi-tree"},
    {"slug": "gastronomico", "nombre": "Gastronomía", "descripcion": "Ceviches, mercados y chefs estrella", "icono": "bi-egg-fried"},
    {"slug": "aventura", "nombre": "Aventura", "descripcion": "Senderismo, surf y deportes extremos", "icono": "bi-compass"},
    {"slug": "arqueologico", "nombre": "Arqueología", "descripcion": "Huacas y sitios prehispánicos", "icono": "bi-bank2"},
    {"slug": "relax", "nombre": "Relax", "descripcion": "Playas, spas y parques tranquilos", "icono": "bi-water"},
    {"slug": "nocturno", "nombre": "Nocturno", "descripcion": "Bares, clubs y vida nocturna limeña", "icono": "bi-moon-stars"},
]

# nombre, categoria_slug, distrito, direccion, precio (S/.), horario,
# duracion_min, lat, lon, accesible_movilidad_reducida, etiquetas
LUGARES = [
    ("Museo Larco", "cultural", "Pueblo Libre", "Av. Simón Bolívar 1515", 35.00, "09:00 - 22:00", 120, -12.0733, -77.0717, True, ["museo", "precolombino"]),
    ("Malecón de Miraflores", "natural", "Miraflores", "Malecón Cisneros", 0.00, "24 horas", 90, -12.1211, -77.0324, True, ["mirador", "costa"]),
    ("Santuario Arqueológico de Pachacamac", "arqueologico", "Lurín", "Antigua Panamericana Sur km 31.5", 15.00, "09:00 - 17:00", 150, -12.2568, -76.9022, False, ["huaca", "prehispanico"]),
    ("Barranco y Puente de los Suspiros", "cultural", "Barranco", "Bajada de Baños", 0.00, "24 horas", 60, -12.1494, -77.0203, False, ["bohemio", "mirador"]),
    ("Circuito Mágico del Agua", "cultural", "Cercado de Lima", "Parque de la Reserva", 4.00, "15:00 - 22:30", 90, -12.0757, -77.0332, True, ["fuentes", "familiar"]),
    ("Lomas de Lúcumo", "natural", "Pachacamac", "Km 40 Antigua Panamericana Sur", 5.00, "07:00 - 16:00", 180, -12.3350, -76.8200, False, ["senderismo", "estacional"]),
    ("Circuito de Playas Costa Verde", "natural", "Miraflores / Barranco", "Bajada Armendáriz", 0.00, "24 horas", 120, -12.1350, -77.0300, False, ["surf", "playa"]),
    ("Bosque El Olivar", "natural", "San Isidro", "Av. Los Olivos", 0.00, "06:00 - 20:00", 60, -12.0970, -77.0350, True, ["parque", "olivos"]),
    ("Plaza Mayor de Lima", "cultural", "Cercado de Lima", "Plaza Mayor", 0.00, "24 horas", 60, -12.0464, -77.0428, True, ["centro historico", "unesco"]),
    ("Catedral de Lima", "cultural", "Cercado de Lima", "Jr. Carabaya s/n", 15.00, "09:00 - 17:00", 60, -12.0458, -77.0304, True, ["religioso", "colonial"]),
    ("Convento de San Francisco", "cultural", "Cercado de Lima", "Jr. Áncash 300", 15.00, "09:00 - 20:30", 75, -12.0447, -77.0281, False, ["catacumbas", "colonial"]),
    ("Huaca Pucllana", "arqueologico", "Miraflores", "Calle General Borgoño cdra. 8", 20.00, "09:00 - 17:00", 75, -12.1103, -77.0297, True, ["huaca", "prehispanico"]),
    ("Museo de Arte de Lima (MALI)", "cultural", "Cercado de Lima", "Paseo Colón 125", 30.00, "10:00 - 20:00", 120, -12.0619, -77.0364, True, ["museo", "arte"]),
    ("Parque Kennedy", "relax", "Miraflores", "Av. Diagonal", 0.00, "24 horas", 45, -12.1219, -77.0297, True, ["gatos", "artesania"]),
    ("Larcomar", "gastronomico", "Miraflores", "Malecón de la Reserva 610", 0.00, "10:00 - 22:00", 120, -12.1319, -77.0303, True, ["centro comercial", "vista al mar"]),
    ("Mercado Central de Lima", "gastronomico", "Cercado de Lima", "Jr. Ucayali s/n", 0.00, "07:00 - 17:00", 60, -12.0561, -77.0281, False, ["mercado", "insumos"]),
    ("Barrio Chino (Calle Capón)", "gastronomico", "Cercado de Lima", "Jr. Ucayali (Calle Capón)", 0.00, "10:00 - 21:00", 60, -12.0567, -77.0264, False, ["chifa", "cultura china"]),
    ("MATE - Museo Mario Testino", "cultural", "Barranco", "Av. Pedro de Osma 409", 30.00, "10:00 - 18:00", 60, -12.1467, -77.0219, True, ["fotografia", "moda"]),
    ("Puente de Piedra", "cultural", "Rímac", "Jr. Trujillo", 0.00, "24 horas", 30, -12.0433, -77.0281, False, ["colonial", "rio rimac"]),
    ("Playa La Herradura", "aventura", "Chorrillos", "Circuito de Playas", 0.00, "24 horas", 120, -12.1892, -77.0186, False, ["surf", "playa"]),
    ("Pantanos de Villa", "natural", "Chorrillos", "Av. Defensores del Morro s/n", 8.00, "07:00 - 17:00", 120, -12.2167, -77.0167, True, ["humedal", "aves"]),
    ("Parque de las Leyendas", "natural", "San Miguel", "Av. Las Leyendas 580", 15.00, "09:00 - 17:00", 180, -12.0733, -77.0917, True, ["zoologico", "familiar"]),
    ("Cerro San Cristóbal", "aventura", "Rímac", "Cerro San Cristóbal", 10.00, "08:00 - 18:00", 90, -12.0333, -77.0233, False, ["mirador", "teleferico"]),
    ("Complejo Arqueológico Mateo Salado", "arqueologico", "Pueblo Libre", "Av. Amézaga s/n", 0.00, "09:00 - 16:00", 60, -12.0761, -77.0567, False, ["huaca", "prehispanico"]),
]


def generar_slug(nombre: str) -> str:
    slug = nombre.lower()
    slug = re.sub(r"[áàä]", "a", slug)
    slug = re.sub(r"[éèë]", "e", slug)
    slug = re.sub(r"[íìï]", "i", slug)
    slug = re.sub(r"[óòö]", "o", slug)
    slug = re.sub(r"[úùü]", "u", slug)
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return slug


def sembrar():
    db = SessionLocal()
    try:
        categorias_por_slug = {}
        for datos in CATEGORIAS:
            existente = db.query(Categoria).filter_by(slug=datos["slug"]).first()
            if existente:
                categorias_por_slug[datos["slug"]] = existente
                continue
            categoria = Categoria(**datos)
            db.add(categoria)
            db.flush()  # asigna categoria.id sin cerrar la transacción
            categorias_por_slug[datos["slug"]] = categoria
        db.commit()
        print(f"Categorías listas: {len(categorias_por_slug)}")

        creados = 0
        for (nombre, cat_slug, distrito, direccion, precio, horario, duracion,
             lat, lon, accesible, etiquetas) in LUGARES:
            if db.query(Lugar).filter_by(nombre=nombre).first():
                continue

            lugar = Lugar(
                nombre=nombre,
                descripcion=f"{nombre} es uno de los atractivos turísticos de {distrito}, Lima.",
                categoria_id=categorias_por_slug[cat_slug].id,
                distrito=distrito,
                direccion=direccion,
                precio=precio,
                horario=horario,
                duracion_estimada_min=duracion,
                ubicacion=WKTElement(f"POINT({lon} {lat})", srid=4326),
                accesible_movilidad_reducida=accesible,
                imagen_url=f"https://picsum.photos/seed/{generar_slug(nombre)}/480/360",
                etiquetas=etiquetas,
                activo=True,
                fuente_informacion="Datos de ejemplo para el prototipo (Etapa 6)",
            )
            db.add(lugar)
            creados += 1

        db.commit()
        print(f"Lugares nuevos creados: {creados} (de {len(LUGARES)} en la lista)")
    finally:
        db.close()


if __name__ == "__main__":
    sembrar()
