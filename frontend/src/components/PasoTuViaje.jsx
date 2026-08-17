const PRESUPUESTOS = [
  { slug: 'economico', etiqueta: 'Económico', icono: 'bi-piggy-bank' },
  { slug: 'moderado', etiqueta: 'Moderado', icono: 'bi-credit-card-2-front' },
  { slug: 'premium', etiqueta: 'Premium', icono: 'bi-gem' },
]

const GRUPOS = [
  { slug: 'solo', etiqueta: 'Solo', icono: 'bi-person' },
  { slug: 'pareja', etiqueta: 'Pareja', icono: 'bi-heart' },
  { slug: 'familia', etiqueta: 'Familia', icono: 'bi-emoji-smile' },
  { slug: 'amigos', etiqueta: 'Amigos', icono: 'bi-people' },
]

function PasoTuViaje({ formulario, onCambiar }) {
  return (
    <div>
      <label htmlFor="duracion" className="form-label fw-semibold">
        Duración del viaje: <span className="ts-text-primary">{formulario.duracionDias} días</span>
      </label>
      <input
        id="duracion"
        type="range"
        className="form-range mb-1"
        min={1}
        max={7}
        value={formulario.duracionDias}
        onChange={(evento) => onCambiar('duracionDias', Number(evento.target.value))}
      />
      <div className="d-flex justify-content-between small text-muted mb-4">
        <span>1 día</span>
        <span>7 días</span>
      </div>

      <p className="form-label fw-semibold mb-2">Presupuesto</p>
      <div className="row g-2 mb-4">
        {PRESUPUESTOS.map((opcion) => (
          <div className="col-4" key={opcion.slug}>
            <button
              type="button"
              className={`ts-opcion-boton w-100${
                formulario.presupuesto === opcion.slug ? ' ts-opcion-boton--activo' : ''
              }`}
              onClick={() => onCambiar('presupuesto', opcion.slug)}
              aria-pressed={formulario.presupuesto === opcion.slug}
            >
              <i className={`bi ${opcion.icono} d-block mb-1`}></i>
              {opcion.etiqueta}
            </button>
          </div>
        ))}
      </div>

      <p className="form-label fw-semibold mb-2">Tipo de grupo</p>
      <div className="row g-2">
        {GRUPOS.map((opcion) => (
          <div className="col-6 col-md-3" key={opcion.slug}>
            <button
              type="button"
              className={`ts-opcion-boton w-100${
                formulario.tipoGrupo === opcion.slug ? ' ts-opcion-boton--activo' : ''
              }`}
              onClick={() => onCambiar('tipoGrupo', opcion.slug)}
              aria-pressed={formulario.tipoGrupo === opcion.slug}
            >
              <i className={`bi ${opcion.icono} d-block mb-1 fs-5`}></i>
              {opcion.etiqueta}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

export default PasoTuViaje
