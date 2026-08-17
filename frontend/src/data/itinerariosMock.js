// Datos de ejemplo (MOCK) de itinerarios guardados por un usuario.
// Imita la forma que tendrán las tablas "itinerarios" y "detalle_itinerario"
// (Etapa 6): un itinerario tiene varios días, y cada día tiene varias
// paradas con hora, lugar y duración. Se reemplaza en la Etapa 10 por
// llamadas a GET /itinerarios/me y GET /itinerarios/{id}.
const itinerariosMock = [
  {
    id: 1,
    titulo: 'Lima Clásica – 3 días',
    presupuesto: 'moderado',
    fechaInicio: '2026-06-15',
    tipoGrupo: 'pareja',
    dias: [
      {
        numero: 1,
        fecha: '2026-06-15',
        tema: 'Centro Histórico & Cultura',
        paradas: [
          { id: 101, hora: '09:00', nombre: 'Plaza Mayor de Lima', distrito: 'Cercado de Lima', categoria: 'cultural', duracion: '1h' },
          { id: 102, hora: '11:00', nombre: 'Museo Larco', distrito: 'Pueblo Libre', categoria: 'cultural', duracion: '2h' },
          { id: 103, hora: '13:30', nombre: 'Circuito Mágico del Agua', distrito: 'Cercado de Lima', categoria: 'cultural', duracion: '1h', nota: 'Almuerzo cerca' },
          { id: 104, hora: '15:00', nombre: 'Circuito Mágico del Agua', distrito: 'Cercado de Lima', categoria: 'cultural', duracion: '2h', nota: 'Show nocturno' },
        ],
      },
      {
        numero: 2,
        fecha: '2026-06-16',
        tema: 'Miraflores & Costa',
        paradas: [
          { id: 105, hora: '10:00', nombre: 'Malecón de Miraflores', distrito: 'Miraflores', categoria: 'natural', duracion: '1.5h' },
          { id: 106, hora: '12:00', nombre: 'Larcomar', distrito: 'Miraflores', categoria: 'gastronomico', duracion: '1h', nota: 'Almuerzo con vista al mar' },
          { id: 107, hora: '14:00', nombre: 'Costa Verde', distrito: 'Miraflores / Barranco', categoria: 'natural', duracion: '2h' },
          { id: 108, hora: '17:00', nombre: 'Parque Kennedy', distrito: 'Miraflores', categoria: 'cultural', duracion: '1h' },
        ],
      },
      {
        numero: 3,
        fecha: '2026-06-17',
        tema: 'Barranco & Naturaleza',
        paradas: [
          { id: 109, hora: '09:00', nombre: 'Lomas de Lúcumo', distrito: 'Pachacamac', categoria: 'natural', duracion: '3h' },
          { id: 110, hora: '13:00', nombre: 'Barranco & Puente de los Suspiros', distrito: 'Barranco', categoria: 'cultural', duracion: '1h', nota: 'Almuerzo en Barranco' },
          { id: 111, hora: '15:00', nombre: 'Barranco & Puente de los Suspiros', distrito: 'Barranco', categoria: 'cultural', duracion: '1h' },
          { id: 112, hora: '17:00', nombre: 'MATE – Museo Mario Testino', distrito: 'Barranco', categoria: 'cultural', duracion: '1.5h' },
        ],
      },
    ],
    presupuestoEstimado: 'S/. 300–500/día',
    distanciaEstimada: '45–80 km',
    recomendacionIA:
      'Basado en tu perfil de viajero, el mejor momento para visitar el Centro Histórico es entre semana antes del mediodía. Para el Malecón, los jueves y viernes al atardecer tienen menor afluencia.',
  },
  {
    id: 2,
    titulo: 'Lima Arqueológica – 2 días',
    presupuesto: 'economico',
    fechaInicio: '2026-06-20',
    tipoGrupo: 'solo',
    dias: [
      {
        numero: 1,
        fecha: '2026-06-20',
        tema: 'Pachacamac',
        paradas: [
          { id: 201, hora: '09:00', nombre: 'Santuario de Pachacamac', distrito: 'Lurín', categoria: 'arqueologico', duracion: '3h' },
          { id: 202, hora: '13:00', nombre: 'Lomas de Lúcumo', distrito: 'Pachacamac', categoria: 'natural', duracion: '2h', nota: 'Almuerzo cerca' },
        ],
      },
      {
        numero: 2,
        fecha: '2026-06-21',
        tema: 'Miraflores & Pueblo Libre',
        paradas: [
          { id: 203, hora: '09:00', nombre: 'Huaca Pucllana', distrito: 'Miraflores', categoria: 'arqueologico', duracion: '1.5h' },
          { id: 204, hora: '11:30', nombre: 'Museo Larco', distrito: 'Pueblo Libre', categoria: 'cultural', duracion: '2h' },
        ],
      },
    ],
    presupuestoEstimado: 'S/. 120–200/día',
    distanciaEstimada: '30–50 km',
    recomendacionIA:
      'Los sitios arqueológicos reciben menos visitantes en la mañana. Te recomendamos llegar antes de las 10:00 a Pachacamac para evitar el calor del mediodía.',
  },
]

export default itinerariosMock
