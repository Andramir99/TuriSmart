import { solicitar } from './api.js'

export function obtenerCategorias() {
  return solicitar('/categorias')
}
