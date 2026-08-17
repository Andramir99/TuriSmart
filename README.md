# TuriSmart Lima

Plataforma web de turismo inteligente para Lima, Perú. Recomienda atractivos turísticos,
genera itinerarios personalizados y visualiza rutas en un mapa, a partir de las preferencias
del usuario recogidas mediante encuestas. Las interacciones se almacenan para, en fases
posteriores, entrenar un modelo de Machine Learning de recomendación.

Proyecto de tesis — en construcción por etapas.

## Estado actual

Etapa 1 en progreso: estructura del proyecto y herramientas de desarrollo.

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Frontend | React + Vite (JavaScript), Bootstrap 5 |
| Mapas | Leaflet + OpenStreetMap |
| Backend | FastAPI (Python) |
| Base de datos | PostgreSQL + PostGIS |
| Machine Learning | pandas, scikit-learn |
| Comunicación | API REST (JSON) |
| Documentación API | Swagger / OpenAPI (autogenerado por FastAPI) |
| Control de versiones | Git + GitHub |

## Estructura del proyecto

```
turismart/
├── frontend/        # Aplicación React (interfaz de usuario)
├── backend/          # API FastAPI (lógica de negocio, ML, acceso a datos)
├── data/             # Datos crudos y procesados para el modelo de ML
├── .gitignore
└── README.md
```

## Cómo ejecutar el proyecto

(Se documentará al final de cada etapa relevante: Etapa 2 para el frontend,
Etapa 4-5 para el backend y la base de datos.)

## Etapas de desarrollo

1. Preparar herramientas y estructura del proyecto
2. Crear React, Bootstrap y navegación
3. Implementar el diseño de Figma
4. Configurar FastAPI
5. Instalar y conectar PostgreSQL/PostGIS
6. Crear modelos, tablas y datos iniciales
7. Implementar registro e inicio de sesión
8. Implementar preferencias y encuesta
9. Implementar catálogo y recomendador inicial
10. Implementar itinerarios
11. Implementar Leaflet y funciones geográficas
12. Guardar interacciones y valoraciones
13. Preparar el dataset
14. Entrenar y evaluar Machine Learning
15. Integrar el modelo con FastAPI
16. Pruebas, documentación y despliegue
