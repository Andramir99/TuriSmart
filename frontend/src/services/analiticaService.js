import { solicitar } from './api.js'

// Objetivo Específico 4: panel de métricas calculado en vivo sobre
// interacciones, valoraciones e itinerarios reales (reemplaza al mock).
export function obtenerDashboard(token) {
  return solicitar('/analitica/dashboard', { token })
}

// Panel general del administrador (distinto del de arriba: ese es para
// agencias/entidades; este es operativo interno y exige rol "admin").
export function obtenerPanelAdmin(token) {
  return solicitar('/analitica/admin', { token })
}
