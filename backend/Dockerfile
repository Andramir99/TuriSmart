# Imagen de la API (FastAPI). La base de datos (PostgreSQL + PostGIS) y
# el frontend corren en sus propios contenedores — ver docker-compose.yml
# en la raíz del proyecto.
FROM python:3.13-slim

# libpq-dev y gcc: por si alguna dependencia (ej. psycopg2-binary en una
# arquitectura sin wheel precompilada) necesita compilar desde el código
# fuente en vez de instalar un binario ya armado.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY migraciones ./migraciones
COPY alembic.ini .
COPY scripts ./scripts

EXPOSE 8000

# Al arrancar: activa PostGIS si hiciera falta (una base administrada
# como la de Render la entrega vacía; ver scripts/00_...), aplica las
# migraciones pendientes y siembra el catálogo inicial
# (scripts/02_sembrar_datos_iniciales.py es idempotente — no duplica
# nada si ya se sembró antes), recién ahí levanta el servidor. Así el
# contenedor deja la plataforma lista para usar, no solo corriendo y
# vacía.
#
# ${PORT:-8000}: Render asigna el puerto a través de la variable PORT;
# en Docker Compose local esa variable no existe, así que se usa 8000.
CMD ["sh", "-c", "python scripts/00_preparar_extension_postgis.py && alembic upgrade head && python scripts/02_sembrar_datos_iniciales.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
