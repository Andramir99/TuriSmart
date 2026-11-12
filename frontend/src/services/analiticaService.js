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

// Info pública del modelo de ML activo (nombre, versión, métricas, fecha).
export function obtenerEstadoModeloMl(token) {
  return solicitar('/recomendaciones/ml/estado', { token })
}

// Reentrenamiento del modelo KNN. Sin forzar, solo entrena si ya hay
// suficientes valoraciones reales nuevas; con forzar=true entrena de
// inmediato (pensado para demostrarlo sin esperar el umbral).
export function reentrenarModeloMl(token, forzar = false) {
  return solicitar(`/recomendaciones/reentrenar?forzar=${forzar}`, { metodo: 'POST', token })
}
