import { solicitar } from './api.js'

export function crearValoracion(datos, token) {
  return solicitar('/valoraciones', { metodo: 'POST', cuerpo: datos, token })
}
