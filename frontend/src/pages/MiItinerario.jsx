import { useState } from 'react'
import { Link } from 'react-router-dom'
import ItinerarioCard from '../components/ItinerarioCard.jsx'
import itinerariosMockIniciales from '../data/itinerariosMock.js'
import '../styles/itinerario.css'

function MiItinerario() {
  // Estado local solo para poder probar "Eliminar" en la interfaz. No se
  // guarda en ningún lado todavía: al recargar la página vuelve a aparecer.
  // La persistencia real (POST/DELETE /itinerarios) llega en la Etapa 10.
  const [itinerarios, setItinerarios] = useState(itinerariosMockIniciales)

  function eliminarItinerario(id) {
    const itinerario = itinerarios.find((item) => item.id === id)
    const confirmado = window.confirm(`¿Eliminar "${itinerario?.titulo}"? Esta acción no se puede deshacer.`)
    if (confirmado) {
      setItinerarios((actuales) => actuales.filter((item) => item.id !== id))
    }
  }

  return (
    <div className="container py-5">
      <div className="d-flex justify-content-between align-items-start flex-wrap gap-3 mb-4">
        <div>
          <p className="ts-eyebrow mb-1">Gestión de viajes</p>
          <h1 className="ts-heading mb-1">Mis Itinerarios</h1>
          <p className="text-muted mb-0">
            {itinerarios.length} itinerario{itinerarios.length === 1 ? '' : 's'} guardado
            {itinerarios.length === 1 ? '' : 's'}
          </p>
        </div>
        <Link to="/planificar" className="btn btn-ts-primary rounded-pill px-4">
          <i className="bi bi-plus-lg me-1"></i> Nuevo itinerario
        </Link>
      </div>

      <div className="alert alert-light border d-flex align-items-center gap-2 mb-4">
        <i className="bi bi-stars text-danger"></i>
        <span>
          <strong>TuriSmart IA</strong> ha analizado tus preferencias y puede optimizar
          cualquier itinerario automáticamente.
        </span>
      </div>

      <div className="row g-4">
        {itinerarios.map((itinerario) => (
          <div className="col-12 col-md-6 col-lg-4" key={itinerario.id}>
            <ItinerarioCard itinerario={itinerario} onEliminar={eliminarItinerario} />
          </div>
        ))}

        <div className="col-12 col-md-6 col-lg-4">
          <Link
            to="/planificar"
            className="ts-card h-100 d-flex flex-column align-items-center justify-content-center text-center p-4 text-decoration-none ts-nuevo-itinerario"
          >
            <span className="ts-nuevo-itinerario-icon mb-3">
              <i className="bi bi-plus-lg"></i>
            </span>
            <span className="fw-semibold text-body">Nuevo itinerario</span>
          </Link>
        </div>
      </div>
    </div>
  )
}

export default MiItinerario
