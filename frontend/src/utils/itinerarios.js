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

const MESES = [
  'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
  'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
]

const DIAS_SEMANA = ['dom', 'lun', 'mar', 'mié', 'jue', 'vie', 'sáb']

// "2026-06-15" -> "15 de junio de 2026"
export function formatearFechaLarga(fechaISO) {
  const fecha = new Date(`${fechaISO}T00:00:00`)
  return `${fecha.getDate()} de ${MESES[fecha.getMonth()]} de ${fecha.getFullYear()}`
}

// "2026-06-15" -> "lun, 15 jun."
export function formatearFechaCorta(fechaISO) {
  const fecha = new Date(`${fechaISO}T00:00:00`)
  const mesAbreviado = MESES[fecha.getMonth()].slice(0, 3)
  return `${DIAS_SEMANA[fecha.getDay()]}, ${fecha.getDate()} ${mesAbreviado}.`
}

export function totalLugares(itinerario) {
  return itinerario.dias.reduce((total, dia) => total + dia.paradas.length, 0)
}

export function totalActividades(itinerario) {
  // Por ahora cada parada equivale a una actividad; cuando el backend
  // distinga "lugar visitado" de "actividad dentro del lugar" (Etapa 10),
  // este cálculo se ajusta sin tocar los componentes que lo usan.
  return totalLugares(itinerario)
}
