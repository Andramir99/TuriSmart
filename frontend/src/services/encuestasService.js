import { solicitar } from './api.js'

export function enviarEncuesta(datos, token) {
  return solicitar('/encuestas', { metodo: 'POST', cuerpo: datos, token })
}
