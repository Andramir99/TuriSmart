import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import ItinerarioCard from '../components/ItinerarioCard.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import { obtenerMisItinerarios, eliminarItinerario } from '../services/itinerariosService.js'
import { ApiError } from '../services/api.js'
import '../styles/itinerario.css'

function MiItinerario() {
  const { token } = useAuth()
  const [itinerarios, setItinerarios] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')

  const cargar = useCallback(() => {
    setCargando(true)
    setError('')
    obtenerMisItinerarios(token)
      .then(setItinerarios)
      .catch((err) => {
        setError(
          err instanceof ApiError ? err.message : 'No se pudieron cargar tus itinerarios.',
        )
      })
      .finally(() => setCargando(false))
  }, [token])

  useEffect(() => {
    cargar()
  }, [cargar])

  async function manejarEliminar(id) {
    const itinerario = itinerarios.find((item) => item.id === id)
    const confirmado = window.confirm(
      `¿Eliminar "${itinerario?.titulo}"? Esta acción no se puede deshacer.`,
    )
    if (!confirmado) return

    try {
      await eliminarItinerario(id, token)
      setItinerarios((actuales) => actuales.filter((item) => item.id !== id))
    } catch (err) {
      window.alert(err instanceof ApiError ? err.message : 'No se pudo eliminar el itinerario.')
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
          <strong>TuriSmart IA</strong> arma tu itinerario automáticamente a partir de tus
          respuestas en "Planifica tu viaje".
        </span>
      </div>

      {cargando ? (
        <div className="text-center text-muted py-5">
          <span className="spinner-border spinner-border-sm me-2"></span>
          Cargando tus itinerarios...
        </div>
      ) : error ? (
        <div className="alert alert-danger d-flex justify-content-between align-items-center">
          <span>
            <i className="bi bi-exclamation-circle me-1"></i> {error}
          </span>
          <button type="button" className="btn btn-sm btn-outline-danger" onClick={cargar}>
            Reintentar
          </button>
        </div>
      ) : (
        <div className="row g-4">
          {itinerarios.map((itinerario) => (
            <div className="col-12 col-md-6 col-lg-4" key={itinerario.id}>
              <ItinerarioCard itinerario={itinerario} onEliminar={manejarEliminar} />
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
      )}
    </div>
  )
}

export default MiItinerario
