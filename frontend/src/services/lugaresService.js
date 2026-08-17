import { solicitar } from './api.js'

export function obtenerLugares({ categoria, distrito, q, lat, lon, radioKm } = {}) {
  const parametros = new URLSearchParams()
  if (categoria && categoria !== 'todos') parametros.set('categoria', categoria)
  if (distrito) parametros.set('distrito', distrito)
  if (q) parametros.set('q', q)
  // lat/lon activan la búsqueda por cercanía real (PostGIS ST_DWithin,
  // Etapa 11) en vez de traer todo el catálogo.
  if (lat !== undefined && lon !== undefined) {
    parametros.set('lat', lat)
    parametros.set('lon', lon)
    if (radioKm) parametros.set('radio_km', radioKm)
  }

  const query = parametros.toString()
  return solicitar(`/lugares${query ? `?${query}` : ''}`)
}

export function obtenerLugarPorId(id) {
  return solicitar(`/lugares/${id}`)
}
