const PRESUPUESTOS = {
  economico: { etiqueta: 'Económico', clase: 'ts-badge-inline ts-badge--natural' },
  moderado: { etiqueta: 'Moderado', clase: 'ts-badge-inline ts-badge--aventura' },
  premium: { etiqueta: 'Premium', clase: 'ts-badge-inline ts-badge--arqueologico' },
}

export function infoPresupuesto(slug) {
  return PRESUPUESTOS[slug] || PRESUPUESTOS.moderado
}

const GRUPOS = {
  solo: { etiqueta: 'Solo', icono: 'bi-person' },
  pareja: { etiqueta: 'Pareja', icono: 'bi-heart' },
  familia: { etiqueta: 'Familia', icono: 'bi-people' },
  amigos: { etiqueta: 'Amigos', icono: 'bi-people-fill' },
}

export function infoGrupo(slug) {
  return GRUPOS[slug] || GRUPOS.solo
}

// El formateo de fechas se movió a utils/fechas.js porque el Dashboard
// también lo necesita. Se re-exporta aquí para no romper los imports que
// ya existían desde las páginas de itinerarios.
export { formatearFechaLarga, formatearFechaCorta } from './fechas.js'

export function totalLugares(itinerario) {
  return itinerario.dias.reduce((total, dia) => total + dia.paradas.length, 0)
}

export function totalActividades(itinerario) {
  // Por ahora cada parada equivale a una actividad; cuando el backend
  // distinga "lugar visitado" de "actividad dentro del lugar" (Etapa 10),
  // este cálculo se ajusta sin tocar los componentes que lo usan.
  return totalLugares(itinerario)
}
