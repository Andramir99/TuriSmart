"""Siembra (seed) de datos iniciales: categorías + lugares.

Ejecutar UNA vez, con el entorno virtual activado, desde la carpeta backend/:
    python scripts/02_sembrar_datos_iniciales.py

Es idempotente: si una categoría o un lugar con el mismo nombre ya existe,
el script lo actualiza en vez de duplicarlo, así que se puede volver a
correr sin miedo (por ejemplo, después de agregar más lugares a la lista).

El catálogo de nombres de lugares proviene del reporte de atractivos
turísticos de Lima Metropolitana de MINCETUR/SIGMINCETUR (set. 2026). Los
precios, horarios y duraciones son aproximados — sirven para probar el
catálogo y el recomendador, no son datos turísticos oficiales verificados.
Las imágenes son fotografías reales (Wikimedia Commons, licencia libre);
donde no se encontró una foto específica confiable del lugar, se usa un
placeholder determinista (picsum.photos) en vez de arriesgar una imagen
equivocada.
"""

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from geoalchemy2.elements import WKTElement  # noqa: E402

from app.core.seguridad import hash_contrasena  # noqa: E402
from app.database.conexion import SessionLocal  # noqa: E402
from app.models import Categoria, Lugar, Usuario  # noqa: E402

# Cuenta administradora de la plataforma: gestiona el catálogo de
# lugares (POST/PUT/DELETE /lugares, protegidos con obtener_usuario_admin).
# Se siembra acá, no por registro normal, porque POST /auth/registro
# siempre crea cuentas con rol "turista" (ver schemas/usuarios.py) — no
# hay forma de volverse admin desde la propia app, a propósito.
CORREO_ADMIN = "admin@turismart.pe"
CONTRASENA_ADMIN_INICIAL = "TuriSmartAdmin2026"

CATEGORIAS = [
    {"slug": "cultural", "nombre": "Cultura & Historia", "descripcion": "Museos, plazas y arquitectura colonial", "icono": "bi-bank"},
    {"slug": "natural", "nombre": "Naturaleza", "descripcion": "Lomas, parques y costa verde", "icono": "bi-tree"},
    {"slug": "gastronomico", "nombre": "Gastronomía", "descripcion": "Ceviches, mercados y chefs estrella", "icono": "bi-egg-fried"},
    {"slug": "aventura", "nombre": "Aventura", "descripcion": "Senderismo, surf y deportes extremos", "icono": "bi-compass"},
    {"slug": "arqueologico", "nombre": "Arqueología", "descripcion": "Huacas y sitios prehispánicos", "icono": "bi-bank2"},
    {"slug": "relax", "nombre": "Relax", "descripcion": "Playas, spas y parques tranquilos", "icono": "bi-water"},
    {"slug": "nocturno", "nombre": "Nocturno", "descripcion": "Bares, clubs y vida nocturna limeña", "icono": "bi-moon-stars"},
]

# Cada lugar es un dict con todos los campos del catálogo enriquecido.
# servicios es una lista de strings; precio=0 significa entrada gratuita.
LUGARES: list[dict] = [
    # ---------------------------------------------------------- ya existentes (24)
    dict(nombre="Museo Larco", categoria="cultural", distrito="Pueblo Libre", direccion="Av. Simón Bolívar 1515",
         precio=35.00, horario="09:00 - 22:00", duracion=120, lat=-12.0733, lon=-77.0717, accesible=True,
         etiquetas=["museo", "precolombino"], pop=5, tipo="Museo arqueológico",
         corta="Colección precolombina de fama mundial en una mansión virreinal del siglo XVIII.",
         completa="El Museo Larco exhibe una de las colecciones más completas de arte precolombino del Perú, con cerámica, textiles, orfebrería y la célebre Sala Erótica, en una antigua casona virreinal rodeada de jardines.",
         servicios=["estacionamiento", "restaurante", "tienda de souvenirs", "guía turístico", "wifi"],
         recom="Reserva una visita guiada para entender mejor las piezas; el restaurante del jardín es ideal para el almuerzo."),
    dict(nombre="Malecón de Miraflores", categoria="natural", distrito="Miraflores", direccion="Malecón Cisneros",
         precio=0.00, horario="24 horas", duracion=90, lat=-12.1211, lon=-77.0324, accesible=True,
         etiquetas=["mirador", "costa"], pop=4, tipo="Parque y mirador costero",
         corta="Franja de parques frente al mar, con miradores y parapentistas.",
         completa="El Malecón de Miraflores recorre varios kilómetros del acantilado limeño con parques, ciclovías y miradores hacia el Pacífico; es un punto habitual para ver parapente y el atardecer.",
         servicios=["ciclovía", "áreas verdes", "wifi"],
         recom="Ve antes del atardecer para ver los parapentes y el cambio de luz sobre el mar."),
    dict(nombre="Santuario Arqueológico de Pachacamac", categoria="arqueologico", distrito="Lurín",
         direccion="Antigua Panamericana Sur km 31.5", precio=15.00, horario="09:00 - 17:00", duracion=150,
         lat=-12.2568, lon=-76.9022, accesible=False, etiquetas=["huaca", "prehispanico"], pop=5,
         tipo="Sitio arqueológico",
         corta="Centro ceremonial prehispánico habitado por distintas culturas durante más de mil años.",
         completa="Pachacamac fue un importante centro religioso y de peregrinación de la costa central, ocupado por las culturas Lima, Wari, Ychsma e Inca. Incluye pirámides con rampa, el Templo del Sol y un museo de sitio.",
         servicios=["museo de sitio", "estacionamiento", "guía turístico", "tienda de souvenirs"],
         recom="Lleva protector solar y gorra: el recorrido es extenso y mayormente al aire libre."),
    dict(nombre="Barranco y Puente de los Suspiros", categoria="cultural", distrito="Barranco",
         direccion="Bajada de Baños", precio=0.00, horario="24 horas", duracion=60, lat=-12.1494, lon=-77.0203,
         accesible=False, etiquetas=["bohemio", "mirador"], pop=5, tipo="Paseo histórico y cultural",
         corta="Bajada histórica y puente de madera, corazón bohemio de Barranco.",
         completa="El Puente de los Suspiros cruza la Bajada de Baños, una antigua calle empedrada rodeada de casonas, murales y galerías, símbolo del distrito bohemio de Barranco.",
         servicios=["restaurantes cercanos", "arte urbano", "miradores"],
         recom="La tradición dice que debes cruzarlo sin respirar para que se cumpla un deseo."),
    dict(nombre="Circuito Mágico del Agua", categoria="cultural", distrito="Cercado de Lima",
         direccion="Parque de la Reserva", precio=4.00, horario="15:00 - 22:30", duracion=90, lat=-12.0757,
         lon=-77.0332, accesible=True, etiquetas=["fuentes", "familiar"], pop=5,
         tipo="Parque temático y espectáculo nocturno",
         corta="El mayor complejo de fuentes ornamentales del mundo, con shows de luces nocturnos.",
         completa="El Parque de la Reserva alberga 13 fuentes interactivas certificadas por el Guinness World Records, con espectáculos de luz, música y proyecciones todas las noches.",
         servicios=["show de luces", "snacks", "baños"],
         recom="Ve de noche para el show de luces; lleva una muda de ropa si quieres entrar a las fuentes interactivas."),
    dict(nombre="Lomas de Lúcumo", categoria="natural", distrito="Pachacamac", direccion="Km 40 Antigua Panamericana Sur",
         precio=5.00, horario="07:00 - 16:00", duracion=180, lat=-12.3350, lon=-76.8200, accesible=False,
         etiquetas=["senderismo", "estacional"], pop=3, tipo="Ecoturismo y senderismo",
         corta="Colinas que reverdecen con la neblina entre julio y octubre.",
         completa="Las Lomas de Lúcumo son un ecosistema estacional que reverdece con la humedad invernal, con senderos de trekking gestionados por la comunidad local y miradores hacia el valle de Pachacamac.",
         servicios=["guías comunitarios", "senderos señalizados", "miradores"],
         recom="La mejor época para verlas verdes es de julio a septiembre; usa calzado de trekking."),
    dict(nombre="Circuito de Playas Costa Verde", categoria="natural", distrito="Miraflores / Barranco",
         direccion="Bajada Armendáriz", precio=0.00, horario="24 horas", duracion=120, lat=-12.1350, lon=-77.0300,
         accesible=False, etiquetas=["surf", "playa"], pop=4, tipo="Playa y deporte acuático",
         corta="Franja de playas y acantilados que conecta varios distritos costeros de Lima.",
         completa="La Costa Verde une las playas de Miraflores, Barranco, Chorrillos y San Miguel a lo largo del litoral limeño, con zonas para surf, ciclismo y paseos frente al mar.",
         servicios=["alquiler de tablas", "ciclovía", "restaurantes frente al mar"],
         recom="El mar está frío todo el año; si vas a surfear, alquila un traje de neopreno."),
    dict(nombre="Bosque El Olivar", categoria="natural", distrito="San Isidro", direccion="Av. Los Olivos",
         precio=0.00, horario="06:00 - 20:00", duracion=60, lat=-12.0970, lon=-77.0350, accesible=True,
         etiquetas=["parque", "olivos"], pop=3, tipo="Parque histórico",
         corta="Olivar colonial de más de 400 años en pleno San Isidro.",
         completa="El Bosque El Olivar conserva olivos sembrados desde la época virreinal, hoy convertidos en un parque arbolado con senderos, esculturas y una laguna.",
         servicios=["senderos", "bancas", "áreas de picnic"],
         recom="Es un buen lugar para fotografías con luz de atardecer entre los olivos."),
    dict(nombre="Plaza Mayor de Lima", categoria="cultural", distrito="Cercado de Lima", direccion="Plaza Mayor",
         precio=0.00, horario="24 horas", duracion=60, lat=-12.0464, lon=-77.0428, accesible=True,
         etiquetas=["centro historico", "unesco"], pop=5, tipo="Centro histórico",
         corta="Plaza fundacional de Lima, rodeada del Palacio de Gobierno y la Catedral.",
         completa="La Plaza Mayor es el punto donde Francisco Pizarro fundó la ciudad en 1535, rodeada por el Palacio de Gobierno, el Palacio Municipal, el Palacio Arzobispal y la Catedral; Patrimonio de la Humanidad por la UNESCO.",
         servicios=["cambio de guardia", "guía turístico"],
         recom="El cambio de guardia en el Palacio de Gobierno ocurre al mediodía."),
    dict(nombre="Catedral de Lima", categoria="cultural", distrito="Cercado de Lima", direccion="Jr. Carabaya s/n",
         precio=15.00, horario="09:00 - 17:00", duracion=60, lat=-12.0458, lon=-77.0304, accesible=True,
         etiquetas=["religioso", "colonial"], pop=5, tipo="Templo y museo religioso",
         corta="Catedral principal de Lima, con el mausoleo de Francisco Pizarro.",
         completa="La Catedral de Lima combina estilos renacentista, barroco y neoclásico tras varias reconstrucciones por terremotos, y alberga el Museo de Arte Religioso y el mausoleo de Francisco Pizarro.",
         servicios=["museo religioso", "guía turístico", "tienda de souvenirs"],
         recom="La entrada incluye el museo de arte religioso en el segundo piso."),
    dict(nombre="Convento de San Francisco", categoria="cultural", distrito="Cercado de Lima", direccion="Jr. Áncash 300",
         precio=15.00, horario="09:00 - 20:30", duracion=75, lat=-12.0447, lon=-77.0281, accesible=False,
         etiquetas=["catacumbas", "colonial"], pop=5, tipo="Convento y catacumbas",
         corta="Convento colonial famoso por sus catacumbas con miles de restos humanos.",
         completa="El Convento de San Francisco conserva una biblioteca con textos coloniales, claustros con azulejos sevillanos y catacumbas que sirvieron como el primer cementerio de Lima.",
         servicios=["guía turístico obligatorio", "tienda de souvenirs", "biblioteca histórica"],
         recom="El recorrido es solo con guía y dura aproximadamente 45 minutos."),
    dict(nombre="Huaca Pucllana", categoria="arqueologico", distrito="Miraflores", direccion="Calle General Borgoño cdra. 8",
         precio=20.00, horario="09:00 - 17:00", duracion=75, lat=-12.1103, lon=-77.0297, accesible=True,
         etiquetas=["huaca", "prehispanico"], pop=5, tipo="Sitio arqueológico",
         corta="Pirámide preinca de adobe en pleno corazón de Miraflores.",
         completa="Huaca Pucllana fue un centro ceremonial y administrativo de la cultura Lima, construido con técnica de 'librero' en adobes. Incluye museo de sitio y restaurante con vista a la pirámide iluminada de noche.",
         servicios=["museo de sitio", "restaurante", "guía turístico", "tienda de souvenirs"],
         recom="La visita nocturna con la huaca iluminada es una experiencia distinta a la diurna."),
    dict(nombre="Museo de Arte de Lima (MALI)", categoria="cultural", distrito="Cercado de Lima", direccion="Paseo Colón 125",
         precio=30.00, horario="10:00 - 20:00", duracion=120, lat=-12.0619, lon=-77.0364, accesible=True,
         etiquetas=["museo", "arte"], pop=4, tipo="Museo de arte",
         corta="El principal museo de arte peruano, de 3000 años de historia hasta hoy.",
         completa="El MALI reúne más de 17 mil piezas que recorren el arte peruano desde la época precolombina hasta el arte contemporáneo, en un edificio histórico del Palacio de la Exposición.",
         servicios=["cafetería", "tienda de souvenirs", "guía turístico", "exposiciones temporales"],
         recom="Revisa la cartelera de exposiciones temporales antes de ir, suelen cambiar cada pocos meses."),
    dict(nombre="Parque Kennedy", categoria="relax", distrito="Miraflores", direccion="Av. Diagonal", precio=0.00,
         horario="24 horas", duracion=45, lat=-12.1219, lon=-77.0297, accesible=True, etiquetas=["gatos", "artesania"],
         pop=4, tipo="Parque urbano",
         corta="El parque central de Miraflores, conocido por sus gatos y ferias de artesanía.",
         completa="El Parque Kennedy es punto de encuentro en el corazón de Miraflores, famoso por su colonia de gatos callejeros y la feria de artesanías que se instala por las tardes.",
         servicios=["feria de artesanías", "wifi"],
         recom="Buen punto de partida para caminar hacia el malecón de Miraflores."),
    dict(nombre="Larcomar", categoria="gastronomico", distrito="Miraflores", direccion="Malecón de la Reserva 610",
         precio=0.00, horario="10:00 - 22:00", duracion=120, lat=-12.1319, lon=-77.0303, accesible=True,
         etiquetas=["centro comercial", "vista al mar"], pop=4, tipo="Centro comercial y gastronomía",
         corta="Centro comercial construido sobre el acantilado, con vista al mar.",
         completa="Larcomar está excavado en el acantilado de Miraflores, con restaurantes, cines y tiendas con vista directa al océano, uno de los puntos más fotografiados de Lima al atardecer.",
         servicios=["restaurantes", "cine", "wifi", "estacionamiento"],
         recom="Busca mesa en los restaurantes del lado del mar para ver el atardecer."),
    dict(nombre="Mercado Central de Lima", categoria="gastronomico", distrito="Cercado de Lima", direccion="Jr. Ucayali s/n",
         precio=0.00, horario="07:00 - 17:00", duracion=60, lat=-12.0561, lon=-77.0281, accesible=False,
         etiquetas=["mercado", "insumos"], pop=3, tipo="Mercado tradicional",
         corta="Mercado tradicional con los insumos de la gastronomía peruana.",
         completa="El Mercado Central reúne puestos de frutas, pescados, especias e insumos típicos de la cocina peruana, junto al Barrio Chino, en pleno centro histórico.",
         servicios=["puestos de comida", "venta de insumos"],
         recom="Cuida tus pertenencias, es una zona concurrida; ve en grupo de preferencia."),
    dict(nombre="Barrio Chino (Calle Capón)", categoria="gastronomico", distrito="Cercado de Lima",
         direccion="Jr. Ucayali (Calle Capón)", precio=0.00, horario="10:00 - 21:00", duracion=60, lat=-12.0567,
         lon=-77.0264, accesible=False, etiquetas=["chifa", "cultura china"], pop=3, tipo="Barrio gastronómico",
         corta="El barrio chino más antiguo de Sudamérica, cuna de la comida chifa.",
         completa="La Calle Capón concentra chifas, tiendas de productos orientales y el arco chino de bienvenida, testimonio de la migración china que dio origen a la cocina chifa peruana.",
         servicios=["chifas", "tiendas de productos orientales"],
         recom="Prueba un chifa tradicional como el arroz chaufa o el tallarín saltado."),
    dict(nombre="MATE - Museo Mario Testino", categoria="cultural", distrito="Barranco", direccion="Av. Pedro de Osma 409",
         precio=30.00, horario="10:00 - 18:00", duracion=60, lat=-12.1467, lon=-77.0219, accesible=True,
         etiquetas=["fotografia", "moda"], pop=3, tipo="Museo fotográfico",
         corta="Museo fotográfico del reconocido fotógrafo peruano Mario Testino.",
         completa="El MATE exhibe la obra del fotógrafo de moda peruano Mario Testino, con retratos de celebridades y una sala dedicada a la cultura e indumentaria tradicional peruana.",
         servicios=["tienda de souvenirs", "exposiciones temporales"],
         recom="Revisa el horario, suele cerrar los lunes."),
    dict(nombre="Puente de Piedra", categoria="cultural", distrito="Rímac", direccion="Jr. Trujillo", precio=0.00,
         horario="24 horas", duracion=30, lat=-12.0433, lon=-77.0281, accesible=False, etiquetas=["colonial", "rio rimac"],
         pop=2, tipo="Puente histórico",
         corta="El puente colonial que conecta el centro de Lima con el Rímac.",
         completa="El Puente de Piedra cruza el río Rímac uniendo el centro histórico con el tradicional distrito del Rímac, y es uno de los puentes más antiguos de la ciudad, en pie desde la época virreinal.",
         servicios=["mirador al río"],
         recom="Desde el puente se aprecia bien la vista hacia el Cerro San Cristóbal."),
    dict(nombre="Playa La Herradura", categoria="aventura", distrito="Chorrillos", direccion="Circuito de Playas",
         precio=0.00, horario="24 horas", duracion=120, lat=-12.1892, lon=-77.0186, accesible=False,
         etiquetas=["surf", "playa"], pop=3, tipo="Playa y surf",
         corta="Playa de bahía cerrada, popular entre surfistas de Lima.",
         completa="La Herradura es una bahía protegida en Chorrillos, con olas apropiadas para el surf y restaurantes de pescado y marisco frente al mar.",
         servicios=["alquiler de tablas", "restaurantes", "estacionamiento"],
         recom="Los fines de semana de verano se llena rápido; llega temprano si vas en auto."),
    dict(nombre="Pantanos de Villa", categoria="natural", distrito="Chorrillos", direccion="Av. Defensores del Morro s/n",
         precio=8.00, horario="07:00 - 17:00", duracion=120, lat=-12.2167, lon=-77.0167, accesible=True,
         etiquetas=["humedal", "aves"], pop=3, tipo="Reserva natural y avistamiento de aves",
         corta="Humedal costero refugio de más de 200 especies de aves.",
         completa="Los Pantanos de Villa son un refugio de vida silvestre y humedal costero, hogar de aves migratorias y residentes, con senderos elevados y miradores para observación de aves.",
         servicios=["senderos elevados", "miradores", "guía turístico"],
         recom="Lleva binoculares si te interesa el avistamiento de aves."),
    dict(nombre="Parque de las Leyendas", categoria="natural", distrito="San Miguel", direccion="Av. Las Leyendas 580",
         precio=15.00, horario="09:00 - 17:00", duracion=180, lat=-12.0733, lon=-77.0917, accesible=True,
         etiquetas=["zoologico", "familiar"], pop=4, tipo="Zoológico",
         corta="El zoológico más grande de Lima, organizado por regiones del Perú.",
         completa="El Parque de las Leyendas es un zoológico y parque temático que agrupa a sus especies según las regiones naturales del Perú: costa, sierra y selva.",
         servicios=["zoológico", "áreas de picnic", "snacks", "estacionamiento"],
         recom="Planifica medio día completo, el recorrido es extenso."),
    dict(nombre="Cerro San Cristóbal", categoria="aventura", distrito="Rímac", direccion="Cerro San Cristóbal",
         precio=10.00, horario="08:00 - 18:00", duracion=90, lat=-12.0333, lon=-77.0233, accesible=False,
         etiquetas=["mirador", "teleferico"], pop=4, tipo="Mirador",
         corta="Mirador con teleférico y la mejor vista panorámica del centro de Lima.",
         completa="El Cerro San Cristóbal domina el centro histórico de Lima desde sus 400 metros de altura, con una cruz monumental y acceso en bus turístico o teleférico desde el Rímac.",
         servicios=["teleférico", "bus turístico", "mirador"],
         recom="Sube en las primeras horas de la mañana cuando hay menos neblina."),
    dict(nombre="Complejo Arqueológico Mateo Salado", categoria="arqueologico", distrito="Pueblo Libre",
         direccion="Av. Amézaga s/n", precio=0.00, horario="09:00 - 16:00", duracion=60, lat=-12.0761, lon=-77.0567,
         accesible=False, etiquetas=["huaca", "prehispanico"], pop=3, tipo="Sitio arqueológico",
         corta="Conjunto de seis pirámides de adobe entre Pueblo Libre, Breña y Lima.",
         completa="Mateo Salado es un complejo de seis pirámides truncas de la cultura Ichma, parcialmente restauradas, ubicado en un terreno que atraviesa tres distritos del centro de Lima.",
         servicios=["guía turístico", "senderos señalizados"],
         recom="Las visitas guiadas gratuitas se coordinan con el Ministerio de Cultura."),

    # ---------------------------------------------------------- nuevos (25, del catálogo MINCETUR)
    dict(nombre="Biblioteca Municipal Manuel Beingolea", categoria="cultural", distrito="Barranco",
         direccion="Av. Pedro de Osma s/n", precio=0.00, horario="09:00 - 18:00", duracion=30, lat=-12.1489,
         lon=-77.0211, accesible=True, etiquetas=["biblioteca", "arquitectura"], pop=2, tipo="Biblioteca y arquitectura",
         corta="Pequeña biblioteca municipal en una casona republicana de Barranco.",
         completa="La Biblioteca Municipal Manuel Beingolea funciona en una casona tradicional de Barranco y es un espacio tranquilo de lectura, parte del circuito de arquitectura republicana del distrito.",
         servicios=["sala de lectura", "wifi"],
         recom="Combínala con un paseo por el parque municipal de Barranco, está muy cerca."),
    dict(nombre="Iglesia y Convento de Santo Domingo", categoria="cultural", distrito="Cercado de Lima",
         direccion="Jr. Camaná y Conde de Superunda", precio=10.00, horario="09:00 - 13:00 / 15:00 - 18:00",
         duracion=60, lat=-12.0456, lon=-77.0294, accesible=False, etiquetas=["religioso", "colonial"], pop=4,
         tipo="Templo y convento colonial",
         corta="Templo colonial que guarda los restos de Santa Rosa de Lima y San Martín de Porres.",
         completa="La Basílica y Convento de Santo Domingo alberga las reliquias de Santa Rosa de Lima, San Martín de Porres y San Juan Macías, además de claustros coloniales y una torre campanario visitable.",
         servicios=["guía turístico", "tienda de souvenirs"],
         recom="Se puede subir a la torre del campanario para una vista del centro histórico."),
    dict(nombre="Huaca Huallamarca", categoria="arqueologico", distrito="San Isidro",
         direccion="Av. Nicolás de Rivera 201", precio=10.00, horario="09:00 - 17:00", duracion=45, lat=-12.0978,
         lon=-77.0345, accesible=False, etiquetas=["huaca", "prehispanico"], pop=3, tipo="Sitio arqueológico",
         corta="Pirámide de adobe de la cultura Lima, rodeada de las torres modernas de San Isidro.",
         completa="Huaca Huallamarca es una pirámide escalonada de más de 1500 años, con un pequeño museo de sitio que exhibe fardos funerarios y cerámica, en contraste con el moderno San Isidro.",
         servicios=["museo de sitio", "guía turístico"],
         recom="La visita es corta, ideal para combinar con un paseo por San Isidro."),
    dict(nombre="Malecón de Barranco", categoria="cultural", distrito="Barranco", direccion="Malecón Barranco",
         precio=0.00, horario="24 horas", duracion=45, lat=-12.1500, lon=-77.0215, accesible=True,
         etiquetas=["mirador", "costa"], pop=3, tipo="Malecón y mirador",
         corta="Malecón arbolado sobre el acantilado de Barranco, con vista al mar.",
         completa="El Malecón de Barranco recorre el borde del acantilado del distrito, con jardines, miradores y bancas; un punto tranquilo para ver el atardecer lejos del bullicio de Miraflores.",
         servicios=["miradores", "áreas verdes"],
         recom="Es un buen punto para fotos del atardecer con menos turistas que en Miraflores."),
    dict(nombre="Balneario de Ancón", categoria="natural", distrito="Ancón", direccion="Malecón de Ancón",
         precio=0.00, horario="24 horas", duracion=120, lat=-11.7739, lon=-77.1771, accesible=False,
         etiquetas=["playa", "balneario"], pop=2, tipo="Playa y balneario",
         corta="Balneario tradicional al norte de Lima, popular en los veranos limeños.",
         completa="Ancón es uno de los balnearios más antiguos de Lima, con una bahía tranquila usada desde el siglo XIX como destino veraniego, conocido por su malecón y restaurantes de pescado.",
         servicios=["restaurantes de pescado", "alquiler de botes"],
         recom="Queda lejos del centro de Lima (más de una hora); combínalo con otro plan en la misma zona norte."),
    dict(nombre="Museo de los Combatientes del Morro de Arica", categoria="cultural", distrito="Cercado de Lima",
         direccion="Parque de la Reserva", precio=5.00, horario="09:00 - 17:00", duracion=45, lat=-12.0760,
         lon=-77.0335, accesible=True, etiquetas=["museo", "historia militar"], pop=2, tipo="Museo histórico militar",
         corta="Museo dedicado a los héroes de la Guerra del Pacífico.",
         completa="Este museo conserva objetos, uniformes y documentos relacionados con la Guerra del Pacífico, en especial la Batalla del Morro de Arica, homenajeando a los combatientes peruanos.",
         servicios=["guía turístico"],
         recom="Se puede visitar junto con el Circuito Mágico del Agua, están en el mismo parque."),
    dict(nombre="Casona San Marcos", categoria="cultural", distrito="Cercado de Lima",
         direccion="Av. Nicolás de Piérola 1222", precio=0.00, horario="09:00 - 17:00 (lun-vie)", duracion=60,
         lat=-12.0565, lon=-77.0453, accesible=True, etiquetas=["cultural", "universitario"], pop=2,
         tipo="Centro cultural",
         corta="Antiguo campus de la Universidad de San Marcos, hoy centro cultural.",
         completa="La Casona de San Marcos fue la sede histórica de la universidad más antigua de América, y hoy funciona como centro cultural con salas de exposición, patios coloniales y actividades gratuitas.",
         servicios=["salas de exposición", "patios históricos", "actividades culturales"],
         recom="Revisa la agenda cultural, suele tener exposiciones y conciertos gratuitos."),
    dict(nombre="Palacio Legislativo (Congreso)", categoria="cultural", distrito="Cercado de Lima",
         direccion="Plaza Bolívar", precio=0.00, horario="Visitas guiadas coordinadas, lun-vie", duracion=45,
         lat=-12.0497, lon=-77.0344, accesible=True, etiquetas=["historico", "gobierno"], pop=3,
         tipo="Edificio histórico y gobierno",
         corta="Sede del Congreso de la República, frente a la Plaza Bolívar.",
         completa="El Palacio Legislativo alberga al Congreso de la República del Perú desde 1905. Se pueden coordinar visitas guiadas gratuitas para conocer el Hemiciclo y los salones históricos.",
         servicios=["visita guiada (coordinar con anticipación)"],
         recom="Las visitas deben coordinarse previamente con la oficina de relaciones públicas del Congreso."),
    dict(nombre="Puruchuco - Huaquerones", categoria="arqueologico", distrito="Ate",
         direccion="Av. Prolongación Javier Prado Este", precio=10.00, horario="09:00 - 17:00", duracion=60,
         lat=-12.0203, lon=-76.9389, accesible=False, etiquetas=["huaca", "prehispanico"], pop=3,
         tipo="Sitio arqueológico",
         corta="Palacio de un curaca inca restaurado, con un museo de sitio.",
         completa="Puruchuco fue la residencia de un curaca durante el incanato, restaurada para mostrar la arquitectura administrativa inca. El cercano cementerio de Huaquerones reveló cientos de fardos funerarios.",
         servicios=["museo de sitio", "guía turístico"],
         recom="Queda junto a la Panamericana, conviene ir en auto o taxi."),
    dict(nombre="Museo Nacional de Arqueología, Antropología e Historia", categoria="cultural",
         distrito="Pueblo Libre", direccion="Plaza Bolívar s/n", precio=10.00, horario="09:00 - 17:00", duracion=90,
         lat=-12.0719, lon=-77.0639, accesible=True, etiquetas=["museo", "arqueologia"], pop=4,
         tipo="Museo arqueológico",
         corta="El museo más antiguo del Perú, con piezas desde la época lítica hasta la colonia.",
         completa="Fundado en 1822, reúne una de las colecciones arqueológicas más importantes del país, incluyendo el Obelisco Tello, momias y cerámica de las principales culturas prehispánicas.",
         servicios=["guía turístico", "tienda de souvenirs"],
         recom="Combínalo con una visita a Mateo Salado, quedan cerca."),
    dict(nombre="Playa Waikiki", categoria="aventura", distrito="Miraflores", direccion="Circuito de Playas",
         precio=0.00, horario="24 horas", duracion=90, lat=-12.1370, lon=-77.0315, accesible=False,
         etiquetas=["surf", "playa"], pop=3, tipo="Playa y surf",
         corta="Playa de Miraflores conocida por sus olas suaves, ideal para principiantes de surf.",
         completa="Waikiki es una de las playas más concurridas de la Costa Verde en Miraflores, con olas constantes y moderadas que la hacen popular entre quienes están aprendiendo a surfear.",
         servicios=["alquiler de tablas", "clases de surf"],
         recom="Es una buena playa para tomar tu primera clase de surf en Lima."),
    dict(nombre="Antigua Taberna Queirolo", categoria="gastronomico", distrito="Pueblo Libre",
         direccion="Av. San Martín 1090", precio=0.00, horario="12:00 - 23:00", duracion=60, lat=-12.0745,
         lon=-77.0622, accesible=True, etiquetas=["bar historico", "pisco"], pop=2, tipo="Bar histórico",
         corta="Bar y bodega de pisco con más de 100 años de historia.",
         completa="La Antigua Taberna Queirolo funciona desde 1880 como bodega y bar tradicional, famosa por su pisco, vinos de elaboración propia y platos criollos en un ambiente de cantina limeña clásica.",
         servicios=["bar", "comida criolla"],
         recom="Prueba el vino borgoña de la casa, es su especialidad desde hace generaciones."),
    dict(nombre="Parque del Amor", categoria="relax", distrito="Miraflores", direccion="Malecón Cisneros",
         precio=0.00, horario="24 horas", duracion=30, lat=-12.1316, lon=-77.0280, accesible=True,
         etiquetas=["mirador", "escultura"], pop=4, tipo="Parque y mirador",
         corta="Parque con la escultura 'El Beso' y mosaicos inspirados en Gaudí frente al mar.",
         completa="El Parque del Amor es conocido por 'El Beso', una gran escultura de una pareja abrazándose, y por sus bancas cubiertas de mosaicos coloridos, con vista directa al océano.",
         servicios=["miradores", "esculturas"],
         recom="Es un plan clásico para ver el atardecer en pareja."),
    dict(nombre="Museo Pedro de Osma", categoria="cultural", distrito="Barranco", direccion="Av. Pedro de Osma 423",
         precio=30.00, horario="10:00 - 18:00", duracion=90, lat=-12.1479, lon=-77.0215, accesible=True,
         etiquetas=["museo", "arte colonial"], pop=3, tipo="Museo de arte colonial",
         corta="Una de las mejores colecciones de arte colonial y virreinal del Perú.",
         completa="El Museo Pedro de Osma exhibe pintura, escultura y platería de la escuela cuzqueña y el virreinato peruano, en una mansión republicana con jardines, una de las casonas más bellas de Barranco.",
         servicios=["jardines", "tienda de souvenirs", "guía turístico"],
         recom="Los jardines también valen la visita, no solo las salas del museo."),
    dict(nombre="Palacio de Gobierno del Perú", categoria="cultural", distrito="Cercado de Lima",
         direccion="Plaza Mayor", precio=0.00, horario="Visitas guiadas coordinadas", duracion=45, lat=-12.0458,
         lon=-77.0314, accesible=True, etiquetas=["gobierno", "historico"], pop=4, tipo="Edificio de gobierno",
         corta="Sede del Poder Ejecutivo, con el tradicional cambio de guardia.",
         completa="El Palacio de Gobierno, también llamado Casa de Pizarro, es la residencia oficial y sede de trabajo del presidente del Perú. Su cambio de guardia al mediodía es uno de los espectáculos más vistos de la Plaza Mayor.",
         servicios=["cambio de guardia", "visita guiada (coordinar)"],
         recom="El cambio de guardia ocurre todos los días al mediodía frente al palacio."),
    dict(nombre="Cementerio Presbítero Maestro", categoria="cultural", distrito="Cercado de Lima",
         direccion="Jr. Áncash cdra. 17", precio=5.00, horario="08:00 - 17:00", duracion=60, lat=-12.0528,
         lon=-77.0180, accesible=False, etiquetas=["historico", "mausoleos"], pop=2,
         tipo="Patrimonio histórico y funerario",
         corta="El primer cementerio monumental de Sudamérica, con mausoleos de personajes históricos.",
         completa="Inaugurado en 1808, reúne mausoleos de mármol y esculturas de personajes históricos del Perú, incluyendo presidentes y próceres, siendo también un museo al aire libre de arte funerario.",
         servicios=["guía turístico", "recorridos temáticos"],
         recom="Algunos recorridos nocturnos cuentan historias y leyendas del cementerio."),
    dict(nombre="Parque de la Amistad", categoria="relax", distrito="Santiago de Surco", direccion="Av. Primavera",
         precio=0.00, horario="06:00 - 22:00", duracion=60, lat=-12.1176, lon=-76.9930, accesible=True,
         etiquetas=["parque", "familiar"], pop=3, tipo="Parque urbano",
         corta="Uno de los parques más grandes y modernos de Lima, con una locomotora antigua.",
         completa="El Parque de la Amistad es un extenso parque de Surco con lagunas artificiales, áreas de picnic, una locomotora histórica exhibida y amplias zonas verdes.",
         servicios=["áreas de picnic", "juegos infantiles", "ciclovía"],
         recom="Ideal para ir en bicicleta, tiene ciclovías internas extensas."),
    dict(nombre="Museo Oro del Perú y Armas del Mundo", categoria="cultural", distrito="Santiago de Surco",
         direccion="Av. Alonso de Molina 1100", precio=33.00, horario="10:30 - 18:00", duracion=60, lat=-12.1086,
         lon=-76.9775, accesible=True, etiquetas=["museo", "orfebreria"], pop=2, tipo="Museo privado",
         corta="Colección privada de orfebrería precolombina y armas históricas.",
         completa="Este museo privado exhibe piezas de oro y plata de culturas prehispánicas junto a una extensa colección de armas y uniformes militares de distintas épocas y países.",
         servicios=["tienda de souvenirs", "guía turístico"],
         recom="Parte de la colección de orfebrería ha sido cuestionada por su autenticidad; visítalo con curiosidad histórica más que con expectativa académica."),
    dict(nombre="Casa de Aliaga", categoria="cultural", distrito="Cercado de Lima", direccion="Jr. de la Unión 224",
         precio=25.00, horario="09:00 - 17:00 (reserva previa)", duracion=60, lat=-12.0456, lon=-77.0298,
         accesible=False, etiquetas=["colonial", "casona"], pop=3, tipo="Casona colonial",
         corta="La casona colonial habitada más antigua de Sudamérica, de la misma familia desde 1535.",
         completa="La Casa de Aliaga perteneció a Jerónimo de Aliaga, fundador de Lima junto a Pizarro, y ha sido habitada ininterrumpidamente por su misma familia desde 1535, con mobiliario y arquitectura virreinal original.",
         servicios=["visita guiada obligatoria"],
         recom="Las visitas requieren coordinación previa, no se puede ingresar sin reserva."),
    dict(nombre="Lomas de Amancaes", categoria="natural", distrito="Rímac",
         direccion="Circuito Ecoturístico Lomas de Amancaes", precio=0.00, horario="07:00 - 16:00 (estacional)",
         duracion=150, lat=-12.0180, lon=-77.0280, accesible=False, etiquetas=["lomas", "senderismo"], pop=2,
         tipo="Ecoturismo y senderismo",
         corta="Lomas estacionales famosas por sus flores amarillas de amancay.",
         completa="Las Lomas de Amancaes reverdecen entre julio y octubre gracias a la neblina invernal, cubriéndose de la flor amarilla de amancay que da nombre al lugar; cuentan con un circuito ecoturístico.",
         servicios=["senderos guiados", "miradores"],
         recom="Solo florece en temporada de lomas (invierno limeño); fuera de esa época el paisaje es árido."),
    dict(nombre="Parque de la Exposición", categoria="relax", distrito="Cercado de Lima", direccion="Av. 28 de Julio",
         precio=0.00, horario="06:00 - 20:00", duracion=60, lat=-12.0665, lon=-77.0345, accesible=True,
         etiquetas=["parque", "historico"], pop=3, tipo="Parque histórico",
         corta="Parque del siglo XIX con la Sala Alzedo, el Pabellón Morisco y el Museo de Arte Italiano.",
         completa="Construido para la Exposición Internacional de 1872, alberga el Museo de Arte Italiano, el Pabellón Morisco y una glorieta a la que la tradición limeña llama 'la media naranja'.",
         servicios=["museo cercano", "áreas verdes", "anfiteatro"],
         recom="Está al lado del MALI, se pueden visitar ambos el mismo día."),
    dict(nombre="Gran Teatro Nacional", categoria="cultural", distrito="San Borja", direccion="Av. Javier Prado Este 2225",
         precio=0.00, horario="Según cartelera de espectáculos", duracion=120, lat=-12.0894, lon=-77.0019,
         accesible=True, etiquetas=["teatro", "espectaculos"], pop=3, tipo="Teatro y artes escénicas",
         corta="El principal escenario de artes escénicas del Perú.",
         completa="El Gran Teatro Nacional es sede de la Orquesta Sinfónica Nacional, el Ballet Nacional y el Coro Nacional, con programación regular de ópera, ballet, música clásica y espectáculos internacionales.",
         servicios=["boletería", "cafetería", "estacionamiento"],
         recom="Revisa la cartelera con anticipación, las entradas para espectáculos populares se agotan rápido."),
    dict(nombre="Zona Arqueológica Cajamarquilla", categoria="arqueologico", distrito="Lurigancho",
         direccion="Carretera Central km 12.5", precio=5.00, horario="09:00 - 16:00", duracion=60, lat=-11.9922,
         lon=-76.9397, accesible=False, etiquetas=["huaca", "prehispanico"], pop=2, tipo="Sitio arqueológico",
         corta="Una de las ciudades de barro prehispánicas más grandes de la costa central.",
         completa="Cajamarquilla fue un importante centro urbano y de intercambio comercial construido en adobe, ocupado por las culturas Lima, Wari e Ychsma, con calles, plazas y recintos aún visibles.",
         servicios=["guía turístico"],
         recom="Queda algo alejado del centro; conviene ir en auto propio o taxi."),
    dict(nombre="Parque Zonal Huáscar", categoria="relax", distrito="San Juan de Lurigancho",
         direccion="Av. Próceres de la Independencia", precio=4.00, horario="08:00 - 17:00", duracion=90,
         lat=-11.9958, lon=-77.0028, accesible=True, etiquetas=["parque", "familiar"], pop=2,
         tipo="Parque recreativo",
         corta="El principal parque zonal del este de Lima, con lagunas y áreas deportivas.",
         completa="El Parque Zonal Huáscar es uno de los grandes pulmones verdes de San Juan de Lurigancho, con lagunas artificiales, piscinas, áreas deportivas y zonas de picnic.",
         servicios=["piscinas", "áreas deportivas", "áreas de picnic"],
         recom="Los fines de semana suele llenarse de familias; ve temprano si buscas tranquilidad."),
    dict(nombre="Huaca Huantille", categoria="arqueologico", distrito="Magdalena del Mar",
         direccion="Av. Sucre cdra. 11", precio=0.00, horario="09:00 - 16:00", duracion=30, lat=-12.0908,
         lon=-77.0708, accesible=False, etiquetas=["huaca", "prehispanico"], pop=1, tipo="Sitio arqueológico",
         corta="Pequeña huaca de barro en medio de una zona residencial de Magdalena.",
         completa="Huaca Huantille es un montículo arqueológico de la cultura Ychsma, hoy rodeado de viviendas en Magdalena del Mar, ejemplo de cómo el patrimonio prehispánico convive con la ciudad moderna.",
         servicios=[],
         recom="Es una visita corta, ideal para combinar con otros planes en Magdalena o San Miguel."),
]


# Fotos reales de cada lugar (Wikimedia Commons, licencia libre). Donde no
# se encontró una foto confiable y específica del lugar (verificado vía la
# API de Wikipedia/Commons), se deja sin entrada aquí y el script usa un
# placeholder determinista (picsum.photos) — mejor eso que arriesgar una
# imagen que no corresponda al lugar real.
IMAGENES_REALES = {
    "Museo Larco": "https://upload.wikimedia.org/wikipedia/commons/c/c7/Lima_museo_larco.jpg",
    "Malecón de Miraflores": "https://upload.wikimedia.org/wikipedia/commons/9/96/Miraflores_Costa_Verde_Skyline_%28Lima%2C_Peru%29.jpg",
    "Santuario Arqueológico de Pachacamac": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Pachac%C3%A1mac-20.jpg",
    "Barranco y Puente de los Suspiros": "https://upload.wikimedia.org/wikipedia/commons/d/d4/PUENTE_DE_LOS_SUSPIROS.jpg",
    "Circuito Mágico del Agua": "https://upload.wikimedia.org/wikipedia/commons/0/02/Lima%2C_Peru_-_Parque_de_la_Reserva_%28Park_of_the_Reserve%29_02.jpg",
    "Lomas de Lúcumo": "https://upload.wikimedia.org/wikipedia/commons/c/ce/Voluntarios_y_voluntarias_reforestando_huarangos_en_las_Lomas_de_L%C3%BAcumo.jpg",
    "Circuito de Playas Costa Verde": "https://upload.wikimedia.org/wikipedia/commons/c/c5/Panorama_of_Chorrillos%2C_Lima%2C_Peru-Skyline.jpg",
    "Bosque El Olivar": "https://upload.wikimedia.org/wikipedia/commons/7/70/Lima_Peru%2C_Bosque_del_Olivar.jpg",
    "Plaza Mayor de Lima": "https://upload.wikimedia.org/wikipedia/commons/e/e2/La_Plaza_Mayor%2C_Lima%2C_Peru.jpg",
    "Catedral de Lima": "https://upload.wikimedia.org/wikipedia/commons/0/00/Historic_Center_of_Lima_-_54548281854.jpg",
    "Convento de San Francisco": "https://upload.wikimedia.org/wikipedia/commons/a/af/Lima_convento_san_francisco_de_asis.jpg",
    "Huaca Pucllana": "https://upload.wikimedia.org/wikipedia/commons/d/de/Huaca_Pucllana_Miraflores.jpg",
    "Museo de Arte de Lima (MALI)": "https://upload.wikimedia.org/wikipedia/commons/6/6f/El_Museo_de_Arte_de_Lima_%28MALI%29.jpg",
    "Parque Kennedy": "https://upload.wikimedia.org/wikipedia/commons/3/36/Parque_Kennedy_-_Lima%2C_Peru.jpg",
    "Larcomar": "https://upload.wikimedia.org/wikipedia/commons/7/78/Larcomar_Mall.jpg",
    "Mercado Central de Lima": "https://upload.wikimedia.org/wikipedia/commons/9/94/Mercado_Central_de_Lima_22.jpg",
    "Barrio Chino (Calle Capón)": "https://upload.wikimedia.org/wikipedia/commons/7/7c/Lima_Chinatown.jpg",
    "MATE - Museo Mario Testino": "https://upload.wikimedia.org/wikipedia/commons/7/7a/HM_9957-1_fachada_%281%29.jpg",
    "Puente de Piedra": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Lima_R%C3%ADo_R%C3%ADmac_Bridge.jpg",
    "Playa La Herradura": "https://upload.wikimedia.org/wikipedia/commons/d/d9/Master_Bodyboarder.jpg",
    "Pantanos de Villa": "https://upload.wikimedia.org/wikipedia/commons/0/0b/Pantanosdevilla2013.jpg",
    "Parque de las Leyendas": "https://upload.wikimedia.org/wikipedia/commons/5/59/Parque_de_las_leyendas_entrada.jpg",
    "Cerro San Cristóbal": "https://upload.wikimedia.org/wikipedia/commons/1/18/Cerro_San_Crist%C3%B3bal_en_Lima.jpg",
    "Complejo Arqueológico Mateo Salado": "https://upload.wikimedia.org/wikipedia/commons/8/80/Complejo_arqueol%C3%B3gico_Mateo_Salado_-_Lima_01.jpg",
    # --- nuevos ---
    "Biblioteca Municipal Manuel Beingolea": "https://upload.wikimedia.org/wikipedia/commons/2/23/Biblioteca_municipal_de_Barranco.jpg",
    "Iglesia y Convento de Santo Domingo": "https://upload.wikimedia.org/wikipedia/commons/0/04/Bas%C3%ADlica_y_convento_de_Santo_Domingo_2.jpg",
    "Huaca Huallamarca": "https://upload.wikimedia.org/wikipedia/commons/8/83/Huallamarca_Archaeological_site_-_pyramid.jpg",
    "Malecón de Barranco": "https://upload.wikimedia.org/wikipedia/commons/2/2e/Malecon_Barranco_Miraflores.JPG",
    "Museo de los Combatientes del Morro de Arica": "https://upload.wikimedia.org/wikipedia/commons/2/26/Museo_de_los_Combatientes_del_Morro_de_Arica.jpg",
    "Casona San Marcos": "https://upload.wikimedia.org/wikipedia/commons/7/71/CCSM-UNMSM_Casona_de_San_Marcos_y_Parque_Univesitario.jpg",
    "Palacio Legislativo (Congreso)": "https://upload.wikimedia.org/wikipedia/commons/a/a8/Palacio_Legislativo_of_Peru.jpg",
    "Puruchuco - Huaquerones": "https://upload.wikimedia.org/wikipedia/commons/4/48/Puruchuco_Archaeological_site_-_overview.jpg",
    "Museo Nacional de Arqueología, Antropología e Historia": "https://upload.wikimedia.org/wikipedia/commons/9/9b/Plaza_Bolivar._Pueblo_Libre%2C_Lima%2C_Per%C3%BA_01.jpg",
    "Antigua Taberna Queirolo": "https://upload.wikimedia.org/wikipedia/commons/3/34/Antigua_Taberna_Queirolo_%282%29.jpg",
    "Museo Pedro de Osma": "https://upload.wikimedia.org/wikipedia/commons/2/2d/Barranco_Museo_Pedro_de_Osma.jpg",
    "Palacio de Gobierno del Perú": "https://upload.wikimedia.org/wikipedia/commons/d/df/Palacio_de_Gobierno_del_Per%C3%BA_2023.jpg",
    "Cementerio Presbítero Maestro": "https://upload.wikimedia.org/wikipedia/commons/3/36/CapillaPresbiteroMaestro.jpg",
    "Parque de la Amistad": "https://upload.wikimedia.org/wikipedia/commons/6/65/El_Parque_de_la_Amistad_en_Surco_-_Lima%2C_Peru.jpg",
    "Casa de Aliaga": "https://upload.wikimedia.org/wikipedia/commons/d/dd/Casa_de_Aliaga%2C_Lima%2C_Per%C3%BA%2C_2015-07-28%2C_DD_44.JPG",
    "Lomas de Amancaes": "https://upload.wikimedia.org/wikipedia/commons/4/49/Caminata_en_el_Circuito_Ecoturistico_Lomas_de_Amancaes_-_R%C3%ADmac_2019.jpg",
    "Parque de la Exposición": "https://upload.wikimedia.org/wikipedia/commons/b/be/T%C3%B3tem%2C_Parque_de_la_Exposici%C3%B3n.jpg",
    "Gran Teatro Nacional": "https://upload.wikimedia.org/wikipedia/commons/5/56/Museo_de_la_Naci%C3%B3n_y_Teatro_Nacional.jpg",
    "Zona Arqueológica Cajamarquilla": "https://upload.wikimedia.org/wikipedia/commons/1/12/INC_sing_Cajamarquilla.JPG",
    "Huaca Huantille": "https://upload.wikimedia.org/wikipedia/commons/0/0d/Huaca_Huantille.jpg",
    # Sin foto específica confiable todavía: Balneario de Ancón, Playa Waikiki,
    # Parque del Amor, Museo Oro del Perú y Armas del Mundo, Parque Zonal Huáscar.
}


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
            db.flush()
            categorias_por_slug[datos["slug"]] = categoria
        db.commit()
        print(f"Categorías listas: {len(categorias_por_slug)}")

        creados = 0
        actualizados = 0
        for l in LUGARES:
            imagen = IMAGENES_REALES.get(
                l["nombre"], f"https://picsum.photos/seed/{generar_slug(l['nombre'])}/480/360"
            )
            existente = db.query(Lugar).filter_by(nombre=l["nombre"]).first()
            if existente:
                existente.descripcion = l["completa"]
                existente.descripcion_corta = l["corta"]
                existente.tipo_turismo = l["tipo"]
                existente.nivel_popularidad = l["pop"]
                existente.servicios_disponibles = l["servicios"]
                existente.recomendaciones_visitante = l["recom"]
                actualizados += 1
                continue

            lugar = Lugar(
                nombre=l["nombre"],
                descripcion=l["completa"],
                descripcion_corta=l["corta"],
                categoria_id=categorias_por_slug[l["categoria"]].id,
                distrito=l["distrito"],
                direccion=l["direccion"],
                precio=l["precio"],
                horario=l["horario"],
                duracion_estimada_min=l["duracion"],
                tipo_turismo=l["tipo"],
                nivel_popularidad=l["pop"],
                servicios_disponibles=l["servicios"],
                recomendaciones_visitante=l["recom"],
                ubicacion=WKTElement(f"POINT({l['lon']} {l['lat']})", srid=4326),
                accesible_movilidad_reducida=l["accesible"],
                imagen_url=imagen,
                etiquetas=l["etiquetas"],
                activo=True,
                fuente_informacion="MINCETUR/SIGMINCETUR (set. 2026); precio, horario y duración aproximados para el prototipo",
            )
            db.add(lugar)
            creados += 1

        db.commit()
        print(f"Lugares nuevos creados: {creados} / actualizados: {actualizados} (de {len(LUGARES)} en la lista)")

        admin = db.query(Usuario).filter_by(correo=CORREO_ADMIN).first()
        if admin is None:
            admin = Usuario(
                nombre="Administrador TuriSmart",
                correo=CORREO_ADMIN,
                contrasena_hash=hash_contrasena(CONTRASENA_ADMIN_INICIAL),
                rol="admin",
            )
            db.add(admin)
            db.commit()
            print(f"Cuenta administradora creada: {CORREO_ADMIN}")
        else:
            print("Cuenta administradora ya existía.")
    finally:
        db.close()


if __name__ == "__main__":
    sembrar()
