import { solicitar } from './api.js'

export function generarRecomendaciones(datos, token) {
  return solicitar('/recomendaciones', { metodo: 'POST', cuerpo: datos, token })
}

export function obtenerEstadoModeloML() {
  return solicitar('/recomendaciones/ml/estado')
}

// "Recomendados para ti" (Etapa 16): perfil dinámico calculado a partir de
// búsquedas, filtros, clics, me gusta e itinerarios — no de un formulario.
// Exige sesión; sin ella no hay de quién calcular el perfil.
export function obtenerRecomendacionesParaTi(token, cantidad = 10) {
  return solicitar(`/recomendaciones/para-ti?cantidad=${cantidad}`, { token })
}
