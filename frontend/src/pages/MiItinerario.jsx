import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import ItinerarioCard from '../components/ItinerarioCard.jsx'
import RecomendacionCard from '../components/RecomendacionCard.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import { obtenerMisItinerarios, eliminarItinerario } from '../services/itinerariosService.js'
import { generarRecomendacionesML } from '../services/recomendacionesService.js'
import { ApiError } from '../services/api.js'
import '../styles/itinerario.css'

function MiItinerario() {
  const { token } = useAuth()
  const [itinerarios, setItinerarios] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')

  // Recomendador de Machine Learning (Etapa 14-15): a diferencia del de
  // reglas (que usa el wizard), este usa el historial de valoraciones.
  // Por eso puede no tener nada que mostrar todavía (mensaje "avisoIA",
  // no un error) si la persona no calificó ningún lugar aún.
  const [recomendacionesIA, setRecomendacionesIA] = useState([])
  const [cargandoIA, setCargandoIA] = useState(true)
  const [avisoIA, setAvisoIA] = useState('')

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

  useEffect(() => {
    setCargandoIA(true)
    setAvisoIA('')
    generarRecomendacionesML(token)
      .then(setRecomendacionesIA)
      .catch((err) => {
        // Un 409 acá es esperado (sin modelo activo o sin calificaciones
        // todavía) — no es un error real, así que no se muestra como uno.
        setAvisoIA(
          err instanceof ApiError
            ? err.message
            : 'No se pudieron calcular recomendaciones con el modelo entrenado.',
        )
      })
      .finally(() => setCargandoIA(false))
  }, [token])

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

      {/* ---- Recomendado para ti: modelo de ML entrenado (Etapa 14-15) ---- */}
      <div className="mb-5">
        <h2 className="h6 mb-3">
          <i className="bi bi-cpu me-1"></i> Recomendado para ti (según tu historial)
        </h2>

        {cargandoIA ? (
          <p className="text-muted small">
            <span className="spinner-border spinner-border-sm me-2"></span>
            Calculando con el modelo entrenado...
          </p>
        ) : avisoIA ? (
          <div className="alert alert-light border small mb-0">
            <i className="bi bi-info-circle me-1"></i> {avisoIA}
          </div>
        ) : (
          <div className="row g-4">
            {recomendacionesIA.map((recomendacion) => (
              <div className="col-6 col-lg-3" key={recomendacion.lugar.id}>
                <RecomendacionCard recomendacion={recomendacion} />
              </div>
            ))}
          </div>
        )}
      </div>

      <h2 className="h6 mb-3">Tus itinerarios</h2>

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
