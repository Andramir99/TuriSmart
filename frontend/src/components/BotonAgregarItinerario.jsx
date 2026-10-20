import { useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { obtenerMisItinerarios, agregarParada } from '../services/itinerariosService.js'
import { crearInteraccion } from '../services/interaccionesService.js'
import { ApiError } from '../services/api.js'

const ANCHO_PANEL = 280

// Botón reutilizable "Agregar a mi itinerario": lo usan la ficha de
// destino (DestinoDetalle) y las tarjetas de recomendación
// (RecomendacionCard). Abre un panel con los itinerarios reales del
// usuario y agrega el lugar al que elija — a diferencia de un simple
// enlace, esto sí modifica un itinerario existente.
//
// El panel se dibuja con un portal a <body> (position: fixed, calculado
// desde la posición real del botón) en vez de vivir dentro de la tarjeta:
// las tarjetas (.ts-card) tienen overflow:hidden para redondear la
// imagen, así que un panel absoluto anidado ahí adentro quedaba cortado.
function BotonAgregarItinerario({
  lugarId,
  className = 'btn btn-ts-primary rounded-pill px-4',
  etiqueta,
  onAgregado,
  onAbrir,
}) {
  const { token } = useAuth()
  const botonRef = useRef(null)
  const [panelAbierto, setPanelAbierto] = useState(false)
  const [posicion, setPosicion] = useState({ top: 0, left: 0 })
  const [misItinerarios, setMisItinerarios] = useState(null)
  const [cargandoItinerarios, setCargandoItinerarios] = useState(false)
  const [agregando, setAgregando] = useState(false)
  const [itinerarioAgregadoId, setItinerarioAgregadoId] = useState(null)
  const [errorAgregar, setErrorAgregar] = useState('')

  function calcularPosicion() {
    const rect = botonRef.current.getBoundingClientRect()
    let left = rect.left
    if (left + ANCHO_PANEL > window.innerWidth - 12) {
      left = Math.max(12, rect.right - ANCHO_PANEL)
    }
    setPosicion({ top: rect.bottom + 8, left })
  }

  function manejarAbrirPanel(evento) {
    evento.preventDefault()
    evento.stopPropagation()
    if (!panelAbierto) calcularPosicion()
    setPanelAbierto((actual) => !actual)
    setErrorAgregar('')
    onAbrir?.()
    if (misItinerarios === null && token) {
      setCargandoItinerarios(true)
      obtenerMisItinerarios(token)
        .then(setMisItinerarios)
        .catch(() => setMisItinerarios([]))
        .finally(() => setCargandoItinerarios(false))
    }
  }

  // Cierra el panel si cambia el scroll/tamaño de la ventana (su posición
  // quedaría desactualizada) o si se hace clic fuera de él.
  useEffect(() => {
    if (!panelAbierto) return

    function cerrar() {
      setPanelAbierto(false)
    }
    function manejarClicFuera(evento) {
      if (botonRef.current && !botonRef.current.contains(evento.target)) {
        cerrar()
      }
    }

    window.addEventListener('scroll', cerrar, true)
    window.addEventListener('resize', cerrar)
    document.addEventListener('mousedown', manejarClicFuera)
    return () => {
      window.removeEventListener('scroll', cerrar, true)
      window.removeEventListener('resize', cerrar)
      document.removeEventListener('mousedown', manejarClicFuera)
    }
  }, [panelAbierto])

  async function manejarAgregar(itinerario) {
    setAgregando(true)
    setErrorAgregar('')
    try {
      await agregarParada(itinerario.id, { lugar_id: lugarId, dia_numero: 1 }, token)
      crearInteraccion(
        { lugar_id: lugarId, itinerario_id: itinerario.id, tipo_interaccion: 'agregado_itinerario' },
        token,
      ).catch(() => {})
      setItinerarioAgregadoId(itinerario.id)
      onAgregado?.(itinerario)
    } catch (err) {
      setErrorAgregar(err instanceof ApiError ? err.message : 'No se pudo agregar el lugar a ese itinerario.')
    } finally {
      setAgregando(false)
    }
  }

  if (!token) {
    return (
      <Link to="/login" className={className} onClick={(e) => e.stopPropagation()}>
        <i className="bi bi-plus-lg me-1"></i> {etiqueta || 'Inicia sesión para agregarlo'}
      </Link>
    )
  }

  return (
    <>
      <button type="button" ref={botonRef} className={className} onClick={manejarAbrirPanel}>
        <i className="bi bi-plus-lg me-1"></i> {etiqueta || 'Agregar a mi itinerario'}
      </button>

      {panelAbierto &&
        createPortal(
          <div
            className="ts-card p-3 shadow-sm"
            style={{
              position: 'fixed',
              top: posicion.top,
              left: posicion.left,
              zIndex: 1050,
              width: ANCHO_PANEL,
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {itinerarioAgregadoId ? (
              <p className="text-success small mb-0">
                <i className="bi bi-check-circle-fill me-1"></i>
                ¡Agregado! Ya puedes verlo en{' '}
                <Link to={`/itinerario/${itinerarioAgregadoId}`}>tu itinerario</Link>.
              </p>
            ) : cargandoItinerarios ? (
              <p className="small text-muted mb-0">
                <span className="spinner-border spinner-border-sm me-2"></span>
                Cargando tus itinerarios...
              </p>
            ) : misItinerarios && misItinerarios.length > 0 ? (
              <>
                <p className="small fw-semibold mb-2">¿A cuál itinerario lo agrego?</p>
                <div className="d-flex flex-column gap-1">
                  {misItinerarios.map((itinerario) => (
                    <button
                      key={itinerario.id}
                      type="button"
                      className="btn btn-sm btn-light border text-start"
                      disabled={agregando}
                      onClick={() => manejarAgregar(itinerario)}
                    >
                      {itinerario.titulo} <span className="text-muted">({itinerario.total_lugares} lugares)</span>
                    </button>
                  ))}
                </div>
                {errorAgregar && <p className="text-danger small mt-2 mb-0">{errorAgregar}</p>}
              </>
            ) : (
              <p className="small text-muted mb-0">
                Todavía no tienes itinerarios.{' '}
                <Link to="/planificar">Crea uno primero con el asistente</Link>, luego podrás agregarle
                lugares sueltos desde aquí.
              </p>
            )}
          </div>,
          document.body,
        )}
    </>
  )
}

export default BotonAgregarItinerario
