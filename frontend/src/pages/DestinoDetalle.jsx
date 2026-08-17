import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { claseBadgeCategoria } from '../utils/categorias.js'
import { obtenerLugarPorId } from '../services/lugaresService.js'
import { ApiError } from '../services/api.js'

function DestinoDetalle() {
  const { id } = useParams()
  const [destino, setDestino] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    setCargando(true)
    setError('')
    setDestino(null)
    obtenerLugarPorId(id)
      .then(setDestino)
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
  }, [id])

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

          <Link to="/itinerario" className="btn btn-ts-primary rounded-pill px-4">
            <i className="bi bi-plus-lg me-1"></i> Agregar a mi itinerario
          </Link>
        </div>
      </div>
    </div>
  )
}

export default DestinoDetalle
