# TuriSmart Lima

Plataforma web de turismo inteligente para Lima, Perú. Recomienda atractivos turísticos
personalizados mediante Machine Learning, visualiza rutas en un mapa geoespacial real (GIS)
y arma itinerarios de viaje de varios días a partir de las preferencias y el comportamiento
real de cada usuario dentro de la plataforma.

Trabajo de Investigación — Ingeniería de Computación y Sistemas, USMP.

## Tabla de contenidos

- [Estado actual](#estado-actual)
- [Funcionalidades principales](#funcionalidades-principales)
- [Stack tecnológico](#stack-tecnológico)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Cómo ejecutar el proyecto](#cómo-ejecutar-el-proyecto)
  - [Opción A: con Docker (recomendada)](#opción-a-con-docker-recomendada)
  - [Opción B: entorno local manual](#opción-b-entorno-local-manual)
- [Variables de entorno](#variables-de-entorno)
- [Documentación de la API](#documentación-de-la-api)
- [Pipeline de Machine Learning](#pipeline-de-machine-learning)
- [Pruebas](#pruebas)
- [Autores y asesoría](#autores-y-asesoría)

## Estado actual

Prototipo funcional: 18 de 21 historias de usuario completas (157 de 178 story points, ~88 %).
Los cuatro objetivos específicos de la investigación cuentan con evidencia verificable en el
sistema real (ver el documento de tesis, capítulo de Resultados).

Pendiente: pruebas automatizadas del backend y autenticación en dos pasos (2FA) — declarados
como trabajo futuro, sin impacto en el funcionamiento actual del prototipo.

## Funcionalidades principales

- **Catálogo turístico real**: 49 atractivos de Lima Metropolitana (fuente: MINCETUR /
  SIGMINCETUR), cada uno con descripción, precio, horario, servicios, etiquetas, nivel de
  popularidad, recomendación para el visitante y foto real verificada.
- **Mapa GIS interactivo**: lugares georreferenciados con PostGIS, filtro por categoría,
  búsqueda "cerca de mí" (geolocalización + consulta espacial `ST_DWithin`), y modo
  itinerario que traza la ruta día por día con las paradas ya visitadas marcadas.
- **Asistente de planificación (wizard)**: genera un itinerario personalizado en 3 pasos,
  funciona con o sin sesión iniciada; el itinerario solo se guarda en una cuenta si el
  usuario está autenticado.
- **Motor de recomendación híbrido**: combina un modelo KNN de contenido (entrenado con
  scikit-learn) con un perfil dinámico de preferencias por categoría —calculado a partir de
  búsquedas, filtros, clics, tiempo de lectura, "me gusta", itinerarios y valoraciones— y la
  popularidad del lugar, reservando una porción de recomendaciones a explorar categorías
  nuevas (evita la "burbuja" de recomendaciones). Incluye un recomendador por reglas para
  usuarios nuevos sin historial (cold start).
- **Gestión de itinerarios**: crear, ver, eliminar, agregar o quitar un lugar suelto,
  reordenar paradas, marcar paradas como visitadas, renombrar el itinerario, valorar la
  experiencia, exportar y compartir.
- **Panel analítico (dashboard)**: métricas calculadas en vivo sobre datos reales de uso
  (itinerarios creados, valoración promedio, tasa de aceptación de recomendaciones de IA,
  tendencia semanal, distribución por tipo de viaje) — excluye a propósito los datos
  sintéticos de prueba.
- **Privacidad y derechos ARCO**: formulario de acceso, rectificación, cancelación y
  oposición conforme a la Ley N.° 29733; seudonimización de datos de encuestas.
- **Guía de bienvenida interactiva**: tutorial guiado de 4 pasos para cuentas nuevas, y una
  pista de un solo paso en "Mis Itinerarios" para quien todavía no tiene ninguno.

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Frontend | React 18 + Vite, Bootstrap 5, React Router |
| Mapas | Leaflet + OpenStreetMap |
| Gráficos | Chart.js |
| Onboarding | driver.js |
| Backend | FastAPI (Python), SQLAlchemy 2, Alembic (migraciones) |
| Autenticación | JWT (PyJWT) + bcrypt |
| Base de datos | PostgreSQL 18 + PostGIS (datos geoespaciales) |
| Machine Learning | scikit-learn (KNN de contenido), pandas, numpy |
| Pruebas de carga | Locust |
| Documentación de la API | Swagger / OpenAPI (autogenerado por FastAPI) |
| Contenedores | Docker + Docker Compose |
| Control de versiones | Git + GitHub |

## Estructura del proyecto

```
TURISMART V1/
├── backend/
│   ├── app/
│   │   ├── api/            # Endpoints (routers de FastAPI)
│   │   ├── core/           # Configuración, seguridad, geografía, anonimización
│   │   ├── database/       # Conexión y base declarativa de SQLAlchemy
│   │   ├── ml/             # Pesos de interacciones y modelos entrenados (.joblib)
│   │   ├── models/         # Modelos de SQLAlchemy (tablas)
│   │   ├── schemas/        # Esquemas de Pydantic (entrada/salida de la API)
│   │   └── services/       # Lógica de negocio
│   ├── migraciones/        # Migraciones de Alembic
│   ├── scripts/            # Siembra de datos, dataset, entrenamiento del modelo
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # Componentes reutilizables (tarjetas, navbar, mapa...)
│   │   ├── context/        # AuthContext (sesión)
│   │   ├── hooks/          # Hooks personalizados
│   │   ├── pages/          # Una por ruta de la aplicación
│   │   ├── services/       # Llamadas a la API
│   │   ├── styles/         # CSS por página/componente
│   │   └── utils/          # Funciones auxiliares
│   └── Dockerfile
├── data/                   # Datos crudos y procesados para el pipeline de ML
├── docker-compose.yml
├── .env.example             # Plantilla de variables para Docker
└── README.md
```

## Cómo ejecutar el proyecto

### Opción A: con Docker (recomendada)

Requiere tener [Docker](https://www.docker.com/) instalado y corriendo.

```bash
cp .env.example .env
```

Completa `POSTGRES_PASSWORD` y `JWT_SECRET_KEY` en ese `.env` (el mismo archivo indica cómo
generarlos), y luego:

```bash
docker compose up --build
```

Esto levanta la base de datos (PostgreSQL + PostGIS), aplica las migraciones y siembra el
catálogo de 49 lugares automáticamente. Al terminar:

- Frontend: http://localhost:5173
- API / Swagger: http://localhost:8000/docs

### Opción B: entorno local manual

**Backend** (requiere Python 3.13 y PostgreSQL con PostGIS instalado):

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env            # completa DATABASE_URL y JWT_SECRET_KEY
alembic upgrade head
python scripts/02_sembrar_datos_iniciales.py
python -m uvicorn app.main:app --reload
```

**Frontend** (requiere Node.js 20+):

```bash
cd frontend
npm install
cp .env.example .env            # VITE_API_URL=http://127.0.0.1:8000
npm run dev
```

## Variables de entorno

**`backend/.env`** (ver `backend/.env.example`):

| Variable | Descripción |
|---|---|
| `APP_ENV` | `development` o `production` |
| `CORS_ORIGINS` | Orígenes permitidos, separados por coma |
| `DATABASE_URL` | Cadena de conexión a PostgreSQL |
| `JWT_SECRET_KEY` | Clave para firmar los tokens de sesión |
| `JWT_ALGORITMO` | Algoritmo de firma (`HS256`) |
| `JWT_EXPIRA_MINUTOS` | Minutos de validez del token |

**`frontend/.env`** (ver `frontend/.env.example`):

| Variable | Descripción |
|---|---|
| `VITE_API_URL` | URL base del backend |

**`.env`** en la raíz (ver `.env.example`): variables usadas solo por `docker-compose.yml`
(`POSTGRES_PASSWORD`, `JWT_SECRET_KEY`, `FRONTEND_URL`, `VITE_API_URL`).

## Documentación de la API

Con el backend corriendo, la documentación interactiva (Swagger UI) está disponible en
`/docs`, y el esquema OpenAPI en `/openapi.json`. Todos los endpoints están agrupados por
módulo: Auth, Usuarios, Categorías, Preferencias, Encuestas, Lugares, Recomendaciones,
Itinerarios, Valoraciones, Interacciones, Solicitudes ARCO y Analítica.

## Pipeline de Machine Learning

Los scripts de `backend/scripts/` se ejecutan en orden, desde `backend/` con el entorno
virtual activado:

| Script | Propósito |
|---|---|
| `01_crear_base_datos.sql` | Crea el rol y la base de datos, habilita PostGIS (una sola vez) |
| `02_sembrar_datos_iniciales.py` | Siembra categorías y el catálogo de 49 lugares (idempotente) |
| `03_generar_datos_sinteticos.py` | Genera usuarios, encuestas e interacciones sintéticas para tener volumen de prueba (marcadas `es_sintetico=True`, nunca se presentan como datos reales) |
| `04_preparar_dataset.py` | Exporta y anonimiza (seudonimiza) el dataset de entrenamiento a `data/processed/` |
| `05_analisis_exploratorio.py` | Análisis exploratorio de los datos preparados |
| `06_entrenar_modelo.py` | Entrena el modelo KNN de contenido y lo evalúa contra un baseline de popularidad (Precision@5, Recall@5, NDCG@5) |
| `07_activar_modelo.py` | Activa un modelo entrenado para que el backend lo use en producción |

## Pruebas

- **Funcionales end-to-end**: plan de pruebas manual que cubre autenticación, wizard de
  planificación, recomendaciones, gestión de itinerarios y valoraciones (ver el documento de
  tesis, capítulo de Metodología).
- **Carga y rendimiento**: validado con Locust — 30 usuarios concurrentes, 0 % de errores,
  95 % de las solicitudes respondidas en 20 ms (criterio de éxito: menos de 3000 ms). Detalle
  completo en `TuriSmart_Lima_Pruebas_Rendimiento_Carga.docx`.
- **Automatizadas de unidad**: no implementadas todavía (pytest en el backend) — declarado
  como trabajo futuro, proporcional al alcance de un prototipo de tesis.

## Autores y asesoría

- Herrera López, Javier Robinson
- Panduro Álvarez, Marcelo André

Asesor: Mg. José Antonio Wu Chong
