import { Link } from 'react-router-dom'
import {
  infoPresupuesto,
  infoGrupo,
  formatearFechaLarga,
  totalActividades,
} from '../utils/itinerarios.js'

function ItinerarioCard({ itinerario, onEliminar }) {
  const presupuesto = infoPresupuesto(itinerario.presupuesto)
  const grupo = infoGrupo(itinerario.tipoGrupo)
  const dias = itinerario.dias.length
  const actividades = totalActividades(itinerario)

  return (
    <div className="ts-card h-100 p-4 d-flex flex-column">
      <div className="d-flex justify-content-between align-items-start mb-3">
        <h3 className="h5 mb-0">{itinerario.titulo}</h3>
        <span className={presupuesto.clase}>{presupuesto.etiqueta}</span>
      </div>

      <ul className="list-unstyled small text-muted mb-3 d-flex flex-column gap-2">
        <li>
          <i className="bi bi-calendar3 me-2"></i>
          {formatearFechaLarga(itinerario.fechaInicio)}
        </li>
        <li>
          <i className={`bi ${grupo.icono} me-2`}></i>
          {grupo.etiqueta} · {dias} día{dias === 1 ? '' : 's'}
        </li>
        <li>
          <i className="bi bi-geo-alt me-2"></i>
          {actividades} actividades en {dias} día{dias === 1 ? '' : 's'}
        </li>
      </ul>

      <div className="d-flex flex-wrap gap-2 mb-4">
        {itinerario.dias.map((dia) => (
          <span key={dia.numero} className="ts-pill">
            Día {dia.numero}
          </span>
        ))}
      </div>

      <div className="d-flex gap-2 mt-auto">
        <Link to={`/itinerario/${itinerario.id}`} className="btn btn-light border flex-grow-1">
          <i className="bi bi-eye me-1"></i> Ver
        </Link>
        <Link
          to={`/itinerario/${itinerario.id}`}
          className="btn btn-ts-primary flex-grow-1"
          title="La edición completa llega en la Etapa 10"
        >
          <i className="bi bi-pencil me-1"></i> Editar
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
