import { Link } from 'react-router-dom'
import { claseBadgeCategoria } from '../utils/categorias.js'

// Tarjeta de una recomendación del recomendador inicial (Etapa 9): a
// diferencia de DestinoCard, aquí el dato central es el "motivo" — la
// explicación de por qué el sistema sugirió justo este lugar.
function RecomendacionCard({ recomendacion }) {
  const { lugar, motivo, puntuacion } = recomendacion

  return (
    <div className="ts-card h-100">
      <div className="ts-card-img-wrap">
        <img src={lugar.imagen_url} alt={lugar.nombre} className="ts-card-img" loading="lazy" />
        <span className={`ts-badge ${claseBadgeCategoria(lugar.categoria.slug)}`}>
          {lugar.categoria.nombre}
        </span>
      </div>
      <div className="p-3">
        <div className="d-flex justify-content-between align-items-start mb-1">
          <h3 className="ts-card-title mb-0">{lugar.nombre}</h3>
          <span className="ts-badge-inline ts-badge--natural flex-shrink-0">
            {Math.round(puntuacion * 100)}% afinidad
          </span>
        </div>
        <p className="text-muted small mb-2">
          <i className="bi bi-geo-alt"></i> {lugar.distrito}
        </p>
        <p className="small mb-2">
          <i className="bi bi-stars text-danger me-1"></i>
          {motivo}
        </p>
        <Link to={`/explorar/${lugar.id}`} className="ts-link-arrow small">
          Ver más <i className="bi bi-arrow-right"></i>
        </Link>
      </div>
    </div>
  )
}

export default RecomendacionCard
