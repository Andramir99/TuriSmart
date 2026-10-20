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

export function renombrarItinerario(id, titulo, token) {
  return solicitar(`/itinerarios/${id}`, { metodo: 'PATCH', cuerpo: { titulo }, token })
}

export function marcarParadaVisitada(itinerarioId, paradaId, visitado, token) {
  return solicitar(`/itinerarios/${itinerarioId}/paradas/${paradaId}`, {
    metodo: 'PATCH',
    cuerpo: { visitado },
    token,
  })
}

export function reordenarParadas(itinerarioId, diaNumero, ordenIds, token) {
  return solicitar(`/itinerarios/${itinerarioId}/paradas/reordenar`, {
    metodo: 'PUT',
    cuerpo: { dia_numero: diaNumero, orden_ids: ordenIds },
    token,
  })
}

// Agrega UN lugar suelto a un itinerario que ya existe (botón "Agregar a
// mi itinerario" de la ficha de un destino), a diferencia de
// crearItinerario, que arma uno nuevo completo desde el asistente.
export function agregarParada(itinerarioId, datos, token) {
  return solicitar(`/itinerarios/${itinerarioId}/paradas`, {
    metodo: 'POST',
    cuerpo: datos,
    token,
  })
}

export function eliminarParada(itinerarioId, paradaId, token) {
  return solicitar(`/itinerarios/${itinerarioId}/paradas/${paradaId}`, {
    metodo: 'DELETE',
    token,
  })
}
