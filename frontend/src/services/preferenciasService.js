import { solicitar } from './api.js'

export function guardarPreferencias(datos, token) {
  return solicitar('/preferencias', { metodo: 'POST', cuerpo: datos, token })
}
