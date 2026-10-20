# Etapa 1: compila la SPA con Vite.
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .

# Vite "hornea" las variables VITE_* dentro del JS en tiempo de build, no
# en tiempo de ejecución — por eso va como build arg y no como variable
# de entorno del contenedor final. Debe ser una URL alcanzable desde el
# NAVEGADOR del usuario (el puerto publicado del backend), no el nombre
# del servicio dentro de la red de Docker Compose.
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

# Etapa 2: sirve los archivos estáticos ya compilados con nginx.
FROM nginx:1.27-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
