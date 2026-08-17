import { claseBadgeCategoria, etiquetaCategoria } from '../utils/categorias.js'

// Fila del listado lateral del Mapa GIS: miniatura + nombre + distrito +
// rating + categoría. Es distinto de DestinoCard (que es la tarjeta grande
// en grilla de Home/Explorar): aquí necesitamos un formato horizontal y
// compacto porque conviven muchos en una barra lateral angosta.
function DestinoListItem({ destino, activo, onSeleccionar }) {
  return (
    <button
      type="button"
      className={`ts-list-item${activo ? ' ts-list-item--active' : ''}`}
      onClick={() => onSeleccionar(destino.id)}
    >
      <img src={destino.imagen} alt={destino.nombre} className="ts-list-item-img" loading="lazy" />
      <div className="text-start flex-grow-1 min-width-0">
        <p className="mb-0 fw-semibold small text-truncate">{destino.nombre}</p>
        <p className="mb-1 text-muted small text-truncate">
          <i className="bi bi-geo-alt"></i> {destino.distrito}
        </p>
        <div className="d-flex align-items-center gap-2">
          <span className="small">
            <i className="bi bi-star-fill text-warning"></i> {destino.rating.toFixed(1)}
          </span>
          <span className={`ts-badge-inline ${claseBadgeCategoria(destino.categoria)}`}>
            {etiquetaCategoria(destino.categoria)}
          </span>
        </div>
      </div>
    </button>
  )
}

export default DestinoListItem
