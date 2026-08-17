// Datos de ejemplo (MOCK) del Dashboard. Cada bloque imita una consulta de
// agregación distinta que en las Etapas 12-13 se calculará de verdad sobre
// las tablas "interacciones", "valoraciones" e "itinerarios":
//   - estadisticas        -> conteos/promedios simples (COUNT, AVG)
//   - tendenciaSemanal    -> GROUP BY semana
//   - destinosMasVisitados-> GROUP BY lugar, ORDER BY total DESC
//   - metricasUsuario     -> porcentajes sobre el perfil de los usuarios
//   - itinerariosRecientes-> los últimos itinerarios creados
const dashboardMock = {
  actualizadoEn: '2026-08-17',

  estadisticas: [
    {
      id: 'itinerarios',
      icono: 'bi-calendar3',
      colorIcono: '#c1443c',
      fondoIcono: '#fbe7e6',
      valor: '127',
      etiqueta: 'Itinerarios esta semana',
      tendencia: '+14%',
    },
    {
      id: 'nps',
      icono: 'bi-star-fill',
      colorIcono: '#d9822b',
      fondoIcono: '#fdf0e2',
      valor: '87',
      etiqueta: 'Satisfacción NPS',
      tendencia: '+3pts',
    },
    {
      id: 'destino',
      icono: 'bi-geo-alt-fill',
      colorIcono: '#3355cc',
      fondoIcono: '#e8eefc',
      valor: 'Malecón Miraflores',
      etiqueta: 'Destino más recomendado',
      tendencia: '412 visitas',
    },
    {
      id: 'tiempo',
      icono: 'bi-clock-fill',
      colorIcono: '#2e7d32',
      fondoIcono: '#e6f4ea',
      valor: '4.2 min',
      etiqueta: 'Tiempo de planificación',
      tendencia: '-0.8 min',
    },
  ],

  tendenciaSemanal: {
    etiquetas: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4', 'Sem 5', 'Sem 6'],
    consultas: [210, 285, 240, 320, 375, 410],
    itinerarios: [70, 95, 80, 115, 140, 155],
  },

  destinosMasVisitados: [
    { nombre: 'Malecón Miraflores', valor: 412 },
    { nombre: 'Plaza Mayor', valor: 375 },
    { nombre: 'Museo Larco', valor: 330 },
    { nombre: 'Barranco', valor: 295 },
    { nombre: 'Pachacamac', valor: 240 },
    { nombre: 'Larcomar', valor: 215 },
    { nombre: 'Circ. Mágico', valor: 185 },
  ],

  metricasUsuario: [
    { etiqueta: 'Turistas nacionales', valor: 62, color: '#c1443c' },
    { etiqueta: 'Turistas internacionales', valor: 38, color: '#3355cc' },
    { etiqueta: 'Viajes en pareja', valor: 45, color: '#d9822b' },
    { etiqueta: 'Viajes en familia', valor: 28, color: '#2e7d32' },
    { etiqueta: 'Viajes solo', valor: 18, color: '#7b3fb8' },
  ],

  itinerariosRecientes: [
    { id: 1, usuario: 'María G.', color: '#c1443c', destinos: 'Museo Larco, Plaza Mayor, Barranco', dias: 3, satisfaccion: 4.9, fecha: '2026-06-02' },
    { id: 2, usuario: 'Carlos R.', color: '#d9822b', destinos: 'Pachacamac, Lomas de Lúcumo', dias: 2, satisfaccion: 4.7, fecha: '2026-06-01' },
    { id: 3, usuario: 'Laura M.', color: '#3355cc', destinos: 'Malecón, Larcomar, Parque Kennedy', dias: 1, satisfaccion: 4.8, fecha: '2026-06-01' },
    { id: 4, usuario: 'Pedro T.', color: '#2e7d32', destinos: 'Centro Histórico, MATE', dias: 2, satisfaccion: 4.6, fecha: '2026-05-31' },
    { id: 5, usuario: 'Ana V.', color: '#7b3fb8', destinos: 'Costa Verde, Barranco, Chorrillos', dias: 3, satisfaccion: 4.9, fecha: '2026-05-30' },
  ],
}

export default dashboardMock
