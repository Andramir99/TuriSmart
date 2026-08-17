import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import itinerariosMock from '../data/itinerariosMock.js'
import { claseBadgeCategoria, etiquetaCategoria, colorCategoria } from '../utils/categorias.js'
import {
  infoPresupuesto,
  infoGrupo,
  formatearFechaLarga,
  formatearFechaCorta,
  totalLugares,
  totalActividades,
} from '../utils/itinerarios.js'
import '../styles/itinerario.css'

function ItinerarioDetalle() {
  const { id } = useParams()
  const navigate = useNavigate()
  const itinerario = itinerariosMock.find((item) => String(item.id) === id)
  const [diasColapsados, setDiasColapsados] = useState({})

  if (!itinerario) {
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

  const presupuesto = infoPresupuesto(itinerario.presupuesto)
  const grupo = infoGrupo(itinerario.tipoGrupo)

  function alternarDia(numero) {
    setDiasColapsados((actual) => ({ ...actual, [numero]: !actual[numero] }))
  }

  function manejarEliminar() {
    const confirmado = window.confirm(
      `¿Eliminar "${itinerario.titulo}"? Esta acción no se puede deshacer.`,
    )
    if (confirmado) {
      // Sin backend todavía (Etapa 10), así que solo volvemos a la lista.
      navigate('/itinerario')
    }
  }

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
          <span className="ts-badge-inline ts-badge--cultural mb-2 d-inline-block">
            <i className="bi bi-stars me-1"></i> Generado por TuriSmart IA
          </span>
          <h1 className="ts-heading mb-2">{itinerario.titulo}</h1>
          <p className="text-muted mb-0 d-flex flex-wrap gap-3">
            <span>
              <i className="bi bi-calendar3 me-1"></i>
              {formatearFechaLarga(itinerario.fechaInicio)}
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

        <div className="d-flex gap-2">
          <button type="button" className="btn btn-light border">
            <i className="bi bi-share me-1"></i> Compartir
          </button>
          <button type="button" className="btn btn-light border">
            <i className="bi bi-download me-1"></i> PDF
          </button>
          <Link to="/planificar" className="btn btn-ts-primary">
            <i className="bi bi-pencil me-1"></i> Editar
          </Link>
        </div>
      </div>

      <div className="row g-4 mt-2">
        {/* ---- Columna izquierda: días y paradas ---- */}
        <div className="col-12 col-lg-8">
          {itinerario.dias.map((dia) => {
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
                      <span className="d-block fw-semibold">
                        Día {dia.numero}{' '}
                        <span className="text-muted fw-normal">
                          {formatearFechaCorta(dia.fecha)}
                        </span>
                      </span>
                      <span className="d-block small text-muted">{dia.tema}</span>
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
                          style={{ backgroundColor: colorCategoria(parada.categoria) }}
                        ></span>
                        <div className="ts-timeline-card">
                          <img
                            src={`https://picsum.photos/seed/parada-${parada.id}/160/160`}
                            alt={parada.nombre}
                            className="ts-timeline-img"
                            loading="lazy"
                          />
                          <div className="flex-grow-1">
                            <div className="d-flex align-items-center gap-2 mb-1">
                              <span className="fw-semibold small">{parada.hora}</span>
                              <span
                                className={`ts-badge-inline ${claseBadgeCategoria(parada.categoria)}`}
                              >
                                {etiquetaCategoria(parada.categoria)}
                              </span>
                            </div>
                            <p className="mb-1 fw-semibold">{parada.nombre}</p>
                            <p className="mb-0 small text-muted">
                              <i className="bi bi-geo-alt"></i> {parada.distrito} ·{' '}
                              <i className="bi bi-clock"></i> {parada.duracion}
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
              <span className="fw-semibold">{itinerario.dias.length} días</span>
            </div>
            <div className="ts-resumen-row">
              <span className="text-muted">Total de lugares</span>
              <span className="fw-semibold">{totalLugares(itinerario)} destinos</span>
            </div>
            <div className="ts-resumen-row">
              <span className="text-muted">Total actividades</span>
              <span className="fw-semibold">{totalActividades(itinerario)} actividades</span>
            </div>
            <div className="ts-resumen-row">
              <span className="text-muted">Presupuesto estimado</span>
              <span className="fw-semibold">{itinerario.presupuestoEstimado}</span>
            </div>
            <div className="ts-resumen-row">
              <span className="text-muted">Distancia estimada</span>
              <span className="fw-semibold">{itinerario.distanciaEstimada}</span>
            </div>
          </div>

          <div className="ts-ia-box mb-4">
            <p className="fw-semibold mb-2">
              <i className="bi bi-stars me-1 text-danger"></i> TuriSmart IA recomienda
            </p>
            <p className="mb-0">{itinerario.recomendacionIA}</p>
          </div>

          <div className="d-flex flex-column gap-2">
            <button type="button" className="btn btn-light border">
              <i className="bi bi-download me-1"></i> Exportar PDF
            </button>
            <button type="button" className="btn btn-light border">
              <i className="bi bi-share me-1"></i> Compartir itinerario
            </button>
            <Link to="/planificar" className="btn btn-ts-primary">
              <i className="bi bi-pencil me-1"></i> Editar itinerario
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
