import { Link } from 'react-router-dom'
import { infoPresupuesto, infoGrupo, formatearFechaLarga } from '../utils/itinerarios.js'

function ItinerarioCard({ itinerario, onEliminar }) {
  const presupuesto = infoPresupuesto(itinerario.presupuesto)
  const grupo = infoGrupo(itinerario.tipo_grupo)
  const numerosDeDia = Array.from({ length: itinerario.dias }, (_, indice) => indice + 1)

  return (
    <div className="ts-card h-100 p-4 d-flex flex-column">
      <div className="d-flex justify-content-between align-items-start mb-3">
        <h3 className="h5 mb-0">{itinerario.titulo}</h3>
        <span className={presupuesto.clase}>{presupuesto.etiqueta}</span>
      </div>

      <ul className="list-unstyled small text-muted mb-3 d-flex flex-column gap-2">
        <li>
          <i className="bi bi-calendar3 me-2"></i>
          {itinerario.fecha_inicio ? formatearFechaLarga(itinerario.fecha_inicio) : 'Sin fecha definida'}
        </li>
        <li>
          <i className={`bi ${grupo.icono} me-2`}></i>
          {grupo.etiqueta} · {itinerario.dias} día{itinerario.dias === 1 ? '' : 's'}
        </li>
        <li>
          <i className="bi bi-geo-alt me-2"></i>
          {itinerario.total_lugares} lugares en {itinerario.dias} día{itinerario.dias === 1 ? '' : 's'}
        </li>
      </ul>

      <div className="d-flex flex-wrap gap-2 mb-4">
        {numerosDeDia.map((numero) => (
          <span key={numero} className="ts-pill">
            Día {numero}
          </span>
        ))}
      </div>

      <div className="d-flex gap-2 mt-auto">
        <Link to={`/itinerario/${itinerario.id}`} className="btn btn-light border flex-grow-1">
          <i className="bi bi-eye me-1"></i> Ver
        </Link>
        <Link
          to="/planificar"
          className="btn btn-ts-primary flex-grow-1"
          title="Genera un nuevo itinerario; la edición parada por parada llega más adelante"
        >
          <i className="bi bi-plus-lg me-1"></i> Nuevo
        </Link>
        <button
          type="button"
          className="btn btn-outline-danger"
          onClick={() => onEliminar(itinerario.id)}
          aria-label={`Eliminar ${itinerario.titulo}`}
        >
          <i className="bi bi-trash"></i>
        </button>
      </div>
    </div>
  )
}

export default ItinerarioCard
