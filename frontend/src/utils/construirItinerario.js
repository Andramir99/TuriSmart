// Convierte las recomendaciones del recomendador (Etapa 9) en las
// "paradas" que espera POST /itinerarios: reparte los lugares entre los
// días disponibles (round-robin) y les asigna horarios que NUNCA se
// solapan entre sí, avanzando el reloj según la duración de cada lugar.
const HORA_INICIO_JORNADA_MIN = 9 * 60 // 09:00, en minutos desde medianoche
const DURACION_POR_DEFECTO_MIN = 60
const DESCANSO_ENTRE_PARADAS_MIN = 30

function minutosAHoraTexto(minutos) {
  const horas = Math.floor(minutos / 60) % 24
  const mins = minutos % 60
  return `${String(horas).padStart(2, '0')}:${String(mins).padStart(2, '0')}:00`
}

export function construirParadasDesdeRecomendaciones(recomendaciones, dias) {
  const minutoActualPorDia = {}

  return recomendaciones.map((recomendacion, indice) => {
    const diaNumero = (indice % dias) + 1
    const minutoInicio = minutoActualPorDia[diaNumero] ?? HORA_INICIO_JORNADA_MIN
    const duracion = recomendacion.lugar.duracion_estimada_min || DURACION_POR_DEFECTO_MIN
    minutoActualPorDia[diaNumero] = minutoInicio + duracion + DESCANSO_ENTRE_PARADAS_MIN

    return {
      lugar_id: recomendacion.lugar.id,
      dia_numero: diaNumero,
      hora_inicio: minutosAHoraTexto(minutoInicio),
      duracion_min: duracion,
    }
  })
}
