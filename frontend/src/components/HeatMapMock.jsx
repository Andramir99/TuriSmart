// Maqueta visual del mapa de calor de flujos turísticos. Las posiciones e
// intensidades son fijas (no vienen de ninguna consulta todavía). Un mapa
// de calor real necesitaría densidad de interacciones por zona geográfica
// (PostGIS) y una librería de heatmap sobre Leaflet — queda fuera del
// alcance de esta etapa, que solo construye la interfaz.
const PUNTOS_CALOR = [
  { nombre: 'Centro', top: '14%', left: '40%', intensidad: 'alta' },
  { nombre: 'Pueblo Libre', top: '22%', left: '30%', intensidad: 'media' },
  { nombre: 'San Isidro', top: '30%', left: '38%', intensidad: 'media' },
  { nombre: 'Miraflores', top: '44%', left: '35%', intensidad: 'alta' },
  { nombre: 'Barranco', top: '55%', left: '33%', intensidad: 'media' },
  { nombre: 'Pachacamac', top: '80%', left: '64%', intensidad: 'baja' },
]

function HeatMapMock() {
  return (
    <div className="ts-heatmap">
      {PUNTOS_CALOR.map((punto) => (
        <div
          key={punto.nombre}
          className={`ts-heat-blob ts-heat-blob--${punto.intensidad}`}
          style={{ top: punto.top, left: punto.left }}
        >
          <span className="ts-heat-label">{punto.nombre}</span>
        </div>
      ))}
      <span className="ts-heatmap-legend">
        <span className="ts-dot" style={{ backgroundColor: '#e05a4e' }}></span> Alta afluencia
      </span>
    </div>
  )
}

export default HeatMapMock
