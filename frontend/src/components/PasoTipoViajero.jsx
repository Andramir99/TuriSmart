// "opciones" viene del backend (GET /categorias, ver Planificar.jsx) en
// vez de un archivo mock: cada categoría que se agregue desde la base de
// datos aparece aquí sin tocar este componente.
function PasoTipoViajero({ opciones, seleccionados, onAlternar }) {
  return (
    <div className="row g-3">
      {opciones.map((tipo) => {
        const activo = seleccionados.includes(tipo.slug)
        return (
          <div className="col-12 col-md-4" key={tipo.slug}>
            <button
              type="button"
              className={`ts-opcion-card${activo ? ' ts-opcion-card--activa' : ''}`}
              onClick={() => onAlternar(tipo.slug)}
              aria-pressed={activo}
            >
              <span className="ts-opcion-icono">
                <i className={`bi ${tipo.icono || 'bi-tag'}`}></i>
              </span>
              <span className="d-block fw-semibold mb-1">{tipo.nombre}</span>
              <span className="d-block small text-muted">{tipo.descripcion}</span>
              {activo && <i className="bi bi-check-circle-fill ts-opcion-check"></i>}
            </button>
          </div>
        )
      })}
    </div>
  )
}

export default PasoTipoViajero
