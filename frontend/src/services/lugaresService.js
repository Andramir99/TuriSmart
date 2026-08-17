import { solicitar } from './api.js'

export function obtenerLugares({ categoria, distrito, q } = {}) {
  const parametros = new URLSearchParams()
  if (categoria && categoria !== 'todos') parametros.set('categoria', categoria)
  if (distrito) parametros.set('distrito', distrito)
  if (q) parametros.set('q', q)

  const query = parametros.toString()
  return solicitar(`/lugares${query ? `?${query}` : ''}`)
}

export function obtenerLugarPorId(id) {
  return solicitar(`/lugares/${id}`)
}
