import { solicitar } from './api.js'

export function generarRecomendaciones(datos, token) {
  return solicitar('/recomendaciones', { metodo: 'POST', cuerpo: datos, token })
}

// Recomendador de Machine Learning (Etapa 14-15): usa el historial de
// valoraciones del usuario, no preferencias declaradas. Exige sesión.
export function generarRecomendacionesML(token) {
  return solicitar('/recomendaciones/ml', { metodo: 'POST', token })
}

export function obtenerEstadoModeloML() {
  return solicitar('/recomendaciones/ml/estado')
}
