// Funciones de formateo de fechas en español, compartidas por Mis
// Itinerarios y el Dashboard (antes vivían solo en utils/itinerarios.js).
const MESES = [
  'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
  'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
]

const DIAS_SEMANA_CORTO = ['dom', 'lun', 'mar', 'mié', 'jue', 'vie', 'sáb']
const DIAS_SEMANA_LARGO = [
  'domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado',
]

function capitalizar(texto) {
  return texto.charAt(0).toUpperCase() + texto.slice(1)
}

// "2026-06-15" -> "15 de junio de 2026"
export function formatearFechaLarga(fechaISO) {
  const fecha = new Date(`${fechaISO}T00:00:00`)
  return `${fecha.getDate()} de ${MESES[fecha.getMonth()]} de ${fecha.getFullYear()}`
}

// "2026-06-15" -> "lun, 15 jun."
export function formatearFechaCorta(fechaISO) {
  const fecha = new Date(`${fechaISO}T00:00:00`)
  const mesAbreviado = MESES[fecha.getMonth()].slice(0, 3)
  return `${DIAS_SEMANA_CORTO[fecha.getDay()]}, ${fecha.getDate()} ${mesAbreviado}.`
}

// "2026-08-17" -> "Lunes, 17 de agosto de 2026"
export function formatearFechaCompleta(fechaISO) {
  const fecha = new Date(`${fechaISO}T00:00:00`)
  return `${capitalizar(DIAS_SEMANA_LARGO[fecha.getDay()])}, ${fecha.getDate()} de ${MESES[fecha.getMonth()]} de ${fecha.getFullYear()}`
}

// "2026-06-02" -> "02 Jun 2026"
export function formatearFechaTabla(fechaISO) {
  const fecha = new Date(`${fechaISO}T00:00:00`)
  const dia = String(fecha.getDate()).padStart(2, '0')
  const mesAbreviado = capitalizar(MESES[fecha.getMonth()].slice(0, 3))
  return `${dia} ${mesAbreviado} ${fecha.getFullYear()}`
}
