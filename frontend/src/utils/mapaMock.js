// Utilidades para la MAQUETA visual del Mapa GIS (Etapa 3). Todavía no hay
// un mapa real: esto solo "proyecta" coordenadas lat/lon dentro de un
// rectángulo que imita el área de Lima Metropolitana, para poder ubicar
// los marcadores de forma aproximada sobre un fondo oscuro.
//
// En la Etapa 11 este archivo se elimina: Leaflet hace su propia proyección
// real a partir de las mismas coordenadas lat/lon que ya guardamos en
// destinosMock.js (y luego en la tabla "lugares" de PostGIS).
const LIMITES_LIMA = {
  latMax: -12.02, // límite norte aproximado
  latMin: -12.36, // límite sur aproximado
  lonMin: -77.12, // límite oeste aproximado (océano)
  lonMax: -76.8, // límite este aproximado
}

export function proyectarPosicion(lat, lon) {
  const top =
    ((LIMITES_LIMA.latMax - lat) / (LIMITES_LIMA.latMax - LIMITES_LIMA.latMin)) * 100
  const left = ((lon - LIMITES_LIMA.lonMin) / (LIMITES_LIMA.lonMax - LIMITES_LIMA.lonMin)) * 100

  return {
    top: `${Math.min(96, Math.max(4, top))}%`,
    left: `${Math.min(96, Math.max(4, left))}%`,
  }
}

// Etiquetas de distrito puramente decorativas (no vienen de ninguna tabla).
export const ETIQUETAS_DISTRITOS_MOCK = [
  { nombre: 'CERCADO DE LIMA', top: '11%', left: '32%' },
  { nombre: 'SAN ISIDRO', top: '25%', left: '32%' },
  { nombre: 'MIRAFLORES', top: '33%', left: '30%' },
  { nombre: 'BARRANCO', top: '41%', left: '27%' },
  { nombre: 'PACHACAMAC', top: '82%', left: '68%' },
  { nombre: 'OCÉANO PACÍFICO', top: '33%', left: '9%' },
]
