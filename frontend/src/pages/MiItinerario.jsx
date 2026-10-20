import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { driver } from 'driver.js'
import 'driver.js/dist/driver.css'
import '../styles/guiaBienvenida.css'
import ItinerarioCard from '../components/ItinerarioCard.jsx'
import RecomendacionCard from '../components/RecomendacionCard.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import { obtenerMisItinerarios, eliminarItinerario } from '../services/itinerariosService.js'
import { obtenerRecomendacionesParaTi } from '../services/recomendacionesService.js'
import { ApiError } from '../services/api.js'
import '../styles/itinerario.css'

const CLAVE_PISTA_NUEVO_ITINERARIO = 'turismart_pista_nuevo_itinerario_vista'

function MiItinerario() {
  const { token } = useAuth()
  const [itinerarios, setItinerarios] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')

  // Motor híbrido (Etapa 16): perfil dinámico + KNN + popularidad. A
  // diferencia del KNN puro de la Etapa 14-15, este SIEMPRE devuelve algo
  // útil incluso sin valoraciones todavía (usa popularidad como respaldo),
  // así que ya no hace falta mostrar un mensaje de error a un usuario nuevo.
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

  // Pista de un solo paso (a diferencia de GuiaBienvenida, que recorre 4):
  // solo para quien llega aquí sin ningún itinerario todavía, y solo una
  // vez — no depende de si la cuenta es nueva, sino de si esta pantalla en
  // particular está vacía.
  useEffect(() => {
    if (cargando || itinerarios.length > 0) return
    if (localStorage.getItem(CLAVE_PISTA_NUEVO_ITINERARIO) === '1') return

    const marcarVista = () => {
      try {
        localStorage.setItem(CLAVE_PISTA_NUEVO_ITINERARIO, '1')
      } catch {
        // si falla, en el peor caso vuelve a aparecer la próxima vez
      }
    }

    const tourDriver = driver({
      showButtons: ['next'],
      nextBtnText: 'Entendido',
      allowClose: true,
      onNextClick: () => {
        marcarVista()
        tourDriver.destroy()
      },
      onCloseClick: () => {
        marcarVista()
        tourDriver.destroy()
      },
      onDestroyed: marcarVista,
    })

    const idTimeout = setTimeout(() => {
      tourDriver.highlight({
        element: '#hint-nuevo-itinerario',
        popover: {
          title: 'Crea tu primer itinerario',
          description: 'Aquí puedes empezar uno desde cero, o dejar que la IA te lo arme en "Planifica tu viaje".',
          side: 'bottom',
        },
      })
    }, 300)
    return () => clearTimeout(idTimeout)
  }, [cargando, itinerarios.length])

  useEffect(() => {
    setCargandoIA(true)
    setAvisoIA('')
    obtenerRecomendacionesParaTi(token, 8)
      .then(setRecomendacionesIA)
      .catch(() => {
        // No se expone el detalle técnico del error al usuario — solo se
        // avisa que por ahora no hay recomendaciones para mostrar.
        setAvisoIA('No pudimos calcular recomendaciones en este momento. Intenta de nuevo más tarde.')
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
        <Link to="/planificar" id="hint-nuevo-itinerario" className="btn btn-ts-primary rounded-pill px-4">
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

      {/* ---- Recomendado para ti: motor híbrido (Etapa 16) ---- */}
      <div className="mb-5">
        <h2 className="h6 mb-3">
          <i className="bi bi-stars me-1"></i> Recomendado para ti
        </h2>

        {cargandoIA ? (
          <p className="text-muted small">
            <span className="spinner-border spinner-border-sm me-2"></span>
            Armando tus recomendaciones...
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
