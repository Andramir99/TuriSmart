import { solicitar } from './api.js'

export function crearItinerario(datos, token) {
  return solicitar('/itinerarios', { metodo: 'POST', cuerpo: datos, token })
}

export function obtenerMisItinerarios(token) {
  return solicitar('/itinerarios/me', { token })
}

export function obtenerItinerarioPorId(id, token) {
  return solicitar(`/itinerarios/${id}`, { token })
}

export function eliminarItinerario(id, token) {
  return solicitar(`/itinerarios/${id}`, { metodo: 'DELETE', token })
}
