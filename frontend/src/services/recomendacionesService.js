import { solicitar } from './api.js'

export function generarRecomendaciones(datos, token) {
  return solicitar('/recomendaciones', { metodo: 'POST', cuerpo: datos, token })
}
