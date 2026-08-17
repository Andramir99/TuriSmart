import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { claseBadgeCategoria } from '../utils/categorias.js'
import { obtenerLugarPorId } from '../services/lugaresService.js'
import { crearValoracion } from '../services/valoracionesService.js'
import { crearInteraccion } from '../services/interaccionesService.js'
import { useAuth } from '../context/AuthContext.jsx'
import { ApiError } from '../services/api.js'
import EstrellasSelector from '../components/EstrellasSelector.jsx'

function DestinoDetalle() {
  const { id } = useParams()
  const { token } = useAuth()
  const [destino, setDestino] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')

  const [puntuacion, setPuntuacion] = useState(0)
  const [estadoVisita, setEstadoVisita] = useState('')
  const [comentario, setComentario] = useState('')
  const [enviandoValoracion, setEnviandoValoracion] = useState(false)
  const [errorValoracion, setErrorValoracion] = useState('')
  const [valoracionEnviada, setValoracionEnviada] = useState(false)

  useEffect(() => {
    setCargando(true)
    setError('')
    setDestino(null)
    obtenerLugarPorId(id)
      .then((datos) => {
        setDestino(datos)
        // Registro pasivo: "alguien vio este lugar". No bloquea la
        // pantalla ni muestra error si falla — es solo telemetría para
        // el futuro dataset del modelo (Etapa 13-14).
        crearInteraccion({ lugar_id: datos.id, tipo_interaccion: 'vista' }, token).catch(() => {})
      })
      .catch((err) => {
        setError(
          err instanceof ApiError && err.status === 404
            ? 'no_encontrado'
            : err instanceof ApiError
              ? err.message
              : 'No se pudo cargar este lugar.',
        )
      })
      .finally(() => setCargando(false))
    // No metemos "token" en las dependencias a propósito: si el usuario
    // inicia sesión DESPUÉS de que la página ya cargó, no queremos volver
    // a pedir el lugar ni duplicar el registro de "vista".
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  function manejarAgregarAItinerario() {
    if (destino) {
      crearInteraccion({ lugar_id: destino.id, tipo_interaccion: 'clic' }, token).catch(() => {})
    }
  }

  async function manejarEnviarValoracion(evento) {
    evento.preventDefault()
    if (puntuacion === 0) {
      setErrorValoracion('Elige al menos una estrella.')
      return
    }
    setErrorValoracion('')
    setEnviandoValoracion(true)
    try {
      await crearValoracion(
        {
          lugar_id: destino.id,
          puntuacion,
          estado_visita: estadoVisita || null,
          comentario: comentario.trim() || null,
        },
        token,
      )
      setValoracionEnviada(true)
      // El promedio ya cambió en el backend; lo reflejamos también acá
      // sin tener que volver a pedir todo el lugar.
      setDestino((actual) => ({
        ...actual,
        valoracion_promedio:
          (actual.valoracion_promedio * actual.total_valoraciones + puntuacion) /
          (actual.total_valoraciones + 1),
        total_valoraciones: actual.total_valoraciones + 1,
      }))
    } catch (err) {
      setErrorValoracion(
        err instanceof ApiError ? err.message : 'No se pudo guardar tu valoración.',
      )
    } finally {
      setEnviandoValoracion(false)
    }
  }

  if (cargando) {
    return (
      <div className="container py-5 text-center text-muted">
        <span className="spinner-border spinner-border-sm me-2"></span>
        Cargando destino...
      </div>
    )
  }

  if (error === 'no_encontrado' || (!cargando && !destino && !error)) {
    return (
      <div className="container py-5 text-center">
        <p className="ts-eyebrow mb-2">Destino no encontrado</p>
        <h1 className="ts-heading mb-3">No encontramos este lugar</h1>
        <Link to="/explorar" className="btn btn-ts-primary rounded-pill px-4">
          Volver a Explorar
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

  return (
    <div className="container py-5">
      <Link
        to="/explorar"
        className="ts-link-arrow small d-inline-flex align-items-center gap-1 mb-3"
      >
        <i className="bi bi-arrow-left"></i> Volver a Explorar
      </Link>

      <div className="row g-4">
        <div className="col-12 col-lg-7">
          <div
            className="ts-card-img-wrap rounded-4 overflow-hidden"
            style={{ aspectRatio: '16 / 9' }}
          >
            <img src={destino.imagen_url} alt={destino.nombre} className="ts-card-img" />
            <span className={`ts-badge ${claseBadgeCategoria(destino.categoria.slug)}`}>
              {destino.categoria.nombre}
            </span>
          </div>

          {/* ---- Calificar este lugar (Etapa 12) ---- */}
          <div className="ts-card p-4 mt-4">
            <h2 className="h6 mb-3">Calificar este lugar</h2>

            {valoracionEnviada ? (
              <p className="text-success small mb-0">
                <i className="bi bi-check-circle-fill me-1"></i>
                ¡Gracias! Tu valoración quedó guardada.
              </p>
            ) : (
              <form onSubmit={manejarEnviarValoracion}>
                <div className="mb-3">
                  <label className="form-label small fw-semibold d-block">Tu puntuación</label>
                  <EstrellasSelector valor={puntuacion} onCambiar={setPuntuacion} />
                </div>

                <div className="mb-3">
                  <label htmlFor="estadoVisita" className="form-label small fw-semibold">
                    ¿Visitaste este lugar?
                  </label>
                  <select
                    id="estadoVisita"
                    className="form-select form-select-sm"
                    value={estadoVisita}
                    onChange={(evento) => setEstadoVisita(evento.target.value)}
                  >
                    <option value="">No especificar</option>
                    <option value="visitado">Sí, lo visité</option>
                    <option value="descartado">No, lo descarté</option>
                    <option value="pendiente">Todavía lo tengo pendiente</option>
                  </select>
                </div>

                <div className="mb-3">
                  <label htmlFor="comentario" className="form-label small fw-semibold">
                    Comentario (opcional)
                  </label>
                  <textarea
                    id="comentario"
                    className="form-control form-control-sm"
                    rows={2}
                    maxLength={1000}
                    value={comentario}
                    onChange={(evento) => setComentario(evento.target.value)}
                  />
                </div>

                {errorValoracion && (
                  <div className="alert alert-danger small py-2 mb-3">{errorValoracion}</div>
                )}

                <button
                  type="submit"
                  className="btn btn-ts-primary btn-sm"
                  disabled={enviandoValoracion}
                >
                  {enviandoValoracion ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2"></span>
                      Guardando...
                    </>
                  ) : (
                    'Guardar valoración'
                  )}
                </button>
              </form>
            )}
          </div>
        </div>

        <div className="col-12 col-lg-5">
          <h1 className="ts-heading mb-2">{destino.nombre}</h1>
          <p className="text-muted mb-2">
            <i className="bi bi-geo-alt"></i> {destino.distrito}
            {destino.direccion && <> · {destino.direccion}</>}
          </p>
          <p className="mb-3">
            <i className="bi bi-star-fill text-warning"></i> {destino.valoracion_promedio.toFixed(1)}{' '}
            <span className="text-muted">
              ({destino.total_valoraciones.toLocaleString('es-PE')} reseñas)
            </span>
          </p>

          <p className="mb-3">{destino.descripcion}</p>

          <ul className="list-unstyled small text-muted mb-4 d-flex flex-column gap-2">
            {destino.precio !== null && (
              <li>
                <i className="bi bi-cash-coin me-2"></i>
                {destino.precio > 0 ? `S/. ${destino.precio.toFixed(2)}` : 'Entrada libre'}
              </li>
            )}
            {destino.horario && (
              <li>
                <i className="bi bi-clock me-2"></i>
                {destino.horario}
              </li>
            )}
            {destino.duracion_estimada_min && (
              <li>
                <i className="bi bi-hourglass-split me-2"></i>
                Visita estimada: {destino.duracion_estimada_min} min
              </li>
            )}
            {destino.accesible_movilidad_reducida && (
              <li>
                <i className="bi bi-universal-access-circle me-2"></i>
                Accesible para movilidad reducida
              </li>
            )}
          </ul>

          <Link
            to="/itinerario"
            className="btn btn-ts-primary rounded-pill px-4"
            onClick={manejarAgregarAItinerario}
          >
            <i className="bi bi-plus-lg me-1"></i> Agregar a mi itinerario
          </Link>
        </div>
      </div>
    </div>
  )
}

export default DestinoDetalle
