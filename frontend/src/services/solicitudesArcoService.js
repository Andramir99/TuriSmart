import { solicitar } from './api.js'

export function enviarSolicitudArco(datos) {
  return solicitar('/solicitudes-arco', { metodo: 'POST', cuerpo: datos })
}
