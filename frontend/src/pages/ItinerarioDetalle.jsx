import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { obtenerItinerarioPorId, eliminarItinerario } from '../services/itinerariosService.js'
import { claseBadgeCategoria, colorCategoria } from '../utils/categorias.js'
import {
  infoPresupuesto,
  infoGrupo,
  formatearFechaLarga,
  agruparParadasPorDia,
  formatearHora,
} from '../utils/itinerarios.js'
import { ApiError } from '../services/api.js'
import '../styles/itinerario.css'

function ItinerarioDetalle() {
  const { id } = useParams()
  const { token } = useAuth()
  const navigate = useNavigate()

  const [itinerario, setItinerario] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [noEncontrado, setNoEncontrado] = useState(false)
  const [error, setError] = useState('')
  const [diasColapsados, setDiasColapsados] = useState({})

  useEffect(() => {
    setCargando(true)
    setError('')
    setNoEncontrado(false)
    obtenerItinerarioPorId(id, token)
      .then(setItinerario)
      .catch((err) => {
        if (err instanceof ApiError && err.status === 404) {
          setNoEncontrado(true)
        } else {
          setError(err instanceof ApiError ? err.message : 'No se pudo cargar el itinerario.')
        }
      })
      .finally(() => setCargando(false))
  }, [id, token])

  function alternarDia(numero) {
    setDiasColapsados((actual) => ({ ...actual, [numero]: !actual[numero] }))
  }

  async function manejarEliminar() {
    const confirmado = window.confirm(
      `¿Eliminar "${itinerario.titulo}"? Esta acción no se puede deshacer.`,
    )
    if (!confirmado) return

    try {
      await eliminarItinerario(id, token)
      navigate('/itinerario')
    } catch (err) {
      window.alert(err instanceof ApiError ? err.message : 'No se pudo eliminar el itinerario.')
    }
  }

  if (cargando) {
    return (
      <div className="container py-5 text-center text-muted">
        <span className="spinner-border spinner-border-sm me-2"></span>
        Cargando itinerario...
      </div>
    )
  }

  if (noEncontrado) {
    return (
      <div className="container py-5 text-center">
        <p className="ts-eyebrow mb-2">Itinerario no encontrado</p>
        <h1 className="ts-heading mb-3">No encontramos este itinerario</h1>
        <Link to="/itinerario" className="btn btn-ts-primary rounded-pill px-4">
          Volver a Mis Itinerarios
        </Link>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container py-5 text-center">
        <div className="alert alert-danger d-inline-block">
          <i className="bi bi-exclamation-circle me-1"></i> {error}
        </div>
      </div>
    )
  }

  const presupuesto = infoPresupuesto(itinerario.presupuesto)
  const grupo = infoGrupo(itinerario.tipo_grupo)
  const dias = agruparParadasPorDia(itinerario.detalles)

  return (
    <div className="container py-5">
      <Link
        to="/itinerario"
        className="ts-link-arrow small d-inline-flex align-items-center gap-1 mb-3"
      >
        <i className="bi bi-arrow-left"></i> Volver a mis itinerarios
      </Link>

      <div className="d-flex justify-content-between align-items-start flex-wrap gap-3 mb-2">
        <div>
          {itinerario.generado_por_ia && (
            <span className="ts-badge-inline ts-badge--cultural mb-2 d-inline-block">
              <i className="bi bi-stars me-1"></i> Generado por TuriSmart IA
            </span>
          )}
          <h1 className="ts-heading mb-2">{itinerario.titulo}</h1>
          <p className="text-muted mb-0 d-flex flex-wrap gap-3">
            <span>
              <i className="bi bi-calendar3 me-1"></i>
              {itinerario.fecha_inicio ? formatearFechaLarga(itinerario.fecha_inicio) : 'Sin fecha definida'}
            </span>
            <span>
              <i className={`bi ${grupo.icono} me-1`}></i>
              {grupo.etiqueta}
            </span>
            <span>
              <i className="bi bi-wallet2 me-1"></i>
              {presupuesto.etiqueta}
            </span>
          </p>
        </div>
      </div>

      <div className="row g-4 mt-2">
        {/* ---- Columna izquierda: días y paradas ---- */}
        <div className="col-12 col-lg-8">
          {dias.map((dia) => {
            const colapsado = Boolean(diasColapsados[dia.numero])
            return (
              <div className="ts-dia-card" key={dia.numero}>
                <button
                  type="button"
                  className="btn w-100 d-flex justify-content-between align-items-center p-0 border-0 bg-transparent"
                  onClick={() => alternarDia(dia.numero)}
                  aria-expanded={!colapsado}
                >
                  <span className="d-flex align-items-center gap-3">
                    <span className="ts-dia-numero">{dia.numero}</span>
                    <span className="text-start">
                      <span className="d-block fw-semibold">Día {dia.numero}</span>
                    </span>
                  </span>
                  <span className="d-flex align-items-center gap-2 text-muted small">
                    {dia.paradas.length} lugares
                    <i className={`bi bi-chevron-${colapsado ? 'down' : 'up'}`}></i>
                  </span>
                </button>

                {!colapsado && (
                  <div className="ts-timeline mt-3">
                    {dia.paradas.map((parada) => (
                      <div className="ts-timeline-item" key={parada.id}>
                        <span
                          className="ts-timeline-dot"
                          style={{ backgroundColor: colorCategoria(parada.lugar.categoria.slug) }}
                        ></span>
                        <div className="ts-timeline-card">
                          <img
                            src={parada.lugar.imagen_url}
                            alt={parada.lugar.nombre}
                            className="ts-timeline-img"
                            loading="lazy"
                          />
                          <div className="flex-grow-1">
                            <div className="d-flex align-items-center gap-2 mb-1">
                              {parada.hora_inicio && (
                                <span className="fw-semibold small">
                                  {formatearHora(parada.hora_inicio)}
                                </span>
                              )}
                              <span
                                className={`ts-badge-inline ${claseBadgeCategoria(parada.lugar.categoria.slug)}`}
                              >
                                {parada.lugar.categoria.nombre}
                              </span>
                            </div>
                            <Link
                              to={`/explorar/${parada.lugar.id}`}
                              className="mb-1 fw-semibold d-block text-body text-decoration-none"
                            >
                              {parada.lugar.nombre}
                            </Link>
                            <p className="mb-0 small text-muted">
                              <i className="bi bi-geo-alt"></i> {parada.lugar.distrito}
                              {parada.duracion_min && (
                                <>
                                  {' '}
                                  · <i className="bi bi-clock"></i> {parada.duracion_min} min
                                </>
                              )}
                            </p>
                            {parada.nota && (
                              <p className="mb-0 small fst-italic text-muted">"{parada.nota}"</p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* ---- Columna derecha: resumen y recomendación IA ---- */}
        <div className="col-12 col-lg-4">
          <div className="ts-resumen-box mb-4">
            <h2 className="h6 mb-3">Resumen del itinerario</h2>
            <div className="ts-resumen-row">
              <span className="text-muted">Días planificados</span>
              <span className="fw-semibold">{itinerario.dias} días</span>
            </div>
            <div className="ts-resumen-row">
              <span className="text-muted">Total de lugares</span>
              <span className="fw-semibold">{itinerario.detalles.length} destinos</span>
            </div>
            <div className="ts-resumen-row">
              <span className="text-muted">Presupuesto estimado</span>
              <span className="fw-semibold">
                {itinerario.presupuesto_estimado_min !== null
                  ? `S/. ${itinerario.presupuesto_estimado_min.toFixed(0)}–${itinerario.presupuesto_estimado_max.toFixed(0)}`
                  : 'No disponible'}
              </span>
            </div>
            <div className="ts-resumen-row">
              <span className="text-muted">Distancia estimada</span>
              <span className="fw-semibold">
                {itinerario.distancia_estimada_km !== null
                  ? `${itinerario.distancia_estimada_km.toFixed(1)} km`
                  : 'No disponible'}
              </span>
            </div>
          </div>

          {itinerario.recomendacion_ia && (
            <div className="ts-ia-box mb-4">
              <p className="fw-semibold mb-2">
                <i className="bi bi-stars me-1 text-danger"></i> TuriSmart IA recomienda
              </p>
              <p className="mb-0">{itinerario.recomendacion_ia}</p>
            </div>
          )}

          <div className="d-flex flex-column gap-2">
            <Link to="/planificar" className="btn btn-ts-primary">
              <i className="bi bi-plus-lg me-1"></i> Generar uno nuevo
            </Link>
            <button type="button" className="btn btn-outline-danger" onClick={manejarEliminar}>
              <i className="bi bi-trash me-1"></i> Eliminar itinerario
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ItinerarioDetalle
