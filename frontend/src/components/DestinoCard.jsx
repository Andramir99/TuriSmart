import { Link } from 'react-router-dom'
import { claseBadgeCategoria, etiquetaCategoria } from '../utils/categorias.js'

// Tarjeta de destino reutilizable: la usa Home ahora, y más adelante
// también Explorar y Mapa GIS, para no repetir este bloque en cada pantalla.
function DestinoCard({ destino }) {
  return (
    <div className="ts-card h-100">
      <div className="ts-card-img-wrap">
        <img src={destino.imagen} alt={destino.nombre} className="ts-card-img" loading="lazy" />
        <span className={`ts-badge ${claseBadgeCategoria(destino.categoria)}`}>
          {etiquetaCategoria(destino.categoria)}
        </span>
      </div>
      <div className="p-3">
        <h3 className="ts-card-title mb-1">{destino.nombre}</h3>
        <p className="text-muted small mb-2">
          <i className="bi bi-geo-alt"></i> {destino.distrito}
        </p>
        <div className="d-flex justify-content-between align-items-center">
          <span className="small">
            <i className="bi bi-star-fill text-warning"></i> {destino.rating.toFixed(1)}{' '}
            <span className="text-muted">({destino.resenas.toLocaleString('es-PE')})</span>
          </span>
          <Link to={`/explorar/${destino.id}`} className="ts-link-arrow small">
            Ver más <i className="bi bi-arrow-right"></i>
          </Link>
        </div>
      </div>
    </div>
  )
}

export default DestinoCard
