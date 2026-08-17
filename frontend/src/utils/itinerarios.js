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

// El backend (GET /itinerarios/{id}) devuelve "detalles" como una lista
// plana de paradas, cada una con su dia_numero — a diferencia del mock
// anterior, que ya venía agrupado en itinerario.dias[]. Esta función
// arma esa agrupación en el frontend, para no tener que rehacer todo el
// componente de la línea de tiempo.
export function agruparParadasPorDia(detalles) {
  const paradasPorDia = new Map()

  for (const parada of detalles) {
    if (!paradasPorDia.has(parada.dia_numero)) {
      paradasPorDia.set(parada.dia_numero, [])
    }
    paradasPorDia.get(parada.dia_numero).push(parada)
  }

  return Array.from(paradasPorDia.entries())
    .sort(([diaA], [diaB]) => diaA - diaB)
    .map(([numero, paradas]) => ({
      numero,
      paradas: [...paradas].sort((a, b) => a.orden - b.orden),
    }))
}

// "10:30:00" (formato de FastAPI) -> "10:30"
export function formatearHora(horaISO) {
  return horaISO ? horaISO.slice(0, 5) : null
}
