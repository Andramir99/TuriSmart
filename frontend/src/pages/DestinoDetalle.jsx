import { Link, useParams } from 'react-router-dom'
import destinosMock from '../data/destinosMock.js'
import { claseBadgeCategoria, etiquetaCategoria } from '../utils/categorias.js'

function DestinoDetalle() {
  const { id } = useParams()
  const destino = destinosMock.find((item) => String(item.id) === id)

  if (!destino) {
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
            <img src={destino.imagen} alt={destino.nombre} className="ts-card-img" />
            <span className={`ts-badge ${claseBadgeCategoria(destino.categoria)}`}>
              {etiquetaCategoria(destino.categoria)}
            </span>
          </div>
        </div>

        <div className="col-12 col-lg-5">
          <h1 className="ts-heading mb-2">{destino.nombre}</h1>
          <p className="text-muted mb-2">
            <i className="bi bi-geo-alt"></i> {destino.distrito}
          </p>
          <p className="mb-4">
            <i className="bi bi-star-fill text-warning"></i> {destino.rating.toFixed(1)}{' '}
            <span className="text-muted">
              ({destino.resenas.toLocaleString('es-PE')} reseñas)
            </span>
          </p>

          <div className="alert alert-light border mb-4">
            <i className="bi bi-info-circle me-1"></i>
            La descripción, horario, precio y dirección exactos llegarán con el catálogo real
            en la Etapa 9 — por ahora estos son datos de ejemplo.
          </div>

          <Link to="/itinerario" className="btn btn-ts-primary rounded-pill px-4">
            <i className="bi bi-plus-lg me-1"></i> Agregar a mi itinerario
          </Link>
        </div>
      </div>
    </div>
  )
}

export default DestinoDetalle
