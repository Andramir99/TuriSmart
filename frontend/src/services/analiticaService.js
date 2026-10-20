import { solicitar } from './api.js'

// Objetivo Específico 4: panel de métricas calculado en vivo sobre
// interacciones, valoraciones e itinerarios reales (reemplaza al mock).
export function obtenerDashboard(token) {
  return solicitar('/analitica/dashboard', { token })
}
