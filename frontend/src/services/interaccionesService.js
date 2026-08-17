import { solicitar } from './api.js'

export function crearInteraccion(datos, token) {
  return solicitar('/interacciones', { metodo: 'POST', cuerpo: datos, token })
}
