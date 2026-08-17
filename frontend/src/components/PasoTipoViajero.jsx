import tiposViajeroMock from '../data/tiposViajeroMock.js'

function PasoTipoViajero({ seleccionados, onAlternar }) {
  return (
    <div className="row g-3">
      {tiposViajeroMock.map((tipo) => {
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
                <i className={`bi ${tipo.icono}`}></i>
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
