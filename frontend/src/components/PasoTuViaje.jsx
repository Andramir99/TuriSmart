import { DISTRITOS_LIMA } from '../utils/distritosLima.js'

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
      <label htmlFor="nombreViaje" className="form-label fw-semibold">
        Nombre de tu viaje <span className="text-muted fw-normal">(opcional)</span>
      </label>
      <p className="small text-muted mb-2">
        Si lo dejas en blanco, le ponemos un nombre automático con la fecha de hoy.
      </p>
      <input
        id="nombreViaje"
        type="text"
        className="form-control mb-4"
        placeholder='Ej. "Cumpleaños de Ana", "Viaje con mis papás"'
        maxLength={150}
        value={formulario.nombreViaje}
        onChange={(evento) => onCambiar('nombreViaje', evento.target.value)}
      />

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

      <label htmlFor="maxLugaresPorDia" className="form-label fw-semibold">
        Máximo de lugares a visitar por día:{' '}
        <span className="ts-text-primary">{formulario.maxLugaresPorDia}</span>
      </label>
      <p className="small text-muted mb-2">
        Así evitamos armarte un día sobrecargado si prefieres visitar pocos lugares con calma.
      </p>
      <input
        id="maxLugaresPorDia"
        type="range"
        className="form-range mb-1"
        min={1}
        max={5}
        value={formulario.maxLugaresPorDia}
        onChange={(evento) => onCambiar('maxLugaresPorDia', Number(evento.target.value))}
      />
      <div className="d-flex justify-content-between small text-muted mb-4">
        <span>1 lugar</span>
        <span>5 lugares</span>
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
      <div className="row g-2 mb-4">
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

      <label htmlFor="numeroPersonas" className="form-label fw-semibold">
        ¿Cuántas personas viajan?
      </label>
      <p className="small text-muted mb-2">
        Cada persona paga su propia entrada, así que esto afecta el presupuesto estimado.
      </p>
      <input
        id="numeroPersonas"
        type="number"
        className="form-control mb-4"
        min={1}
        max={20}
        value={formulario.numeroPersonas}
        onChange={(evento) => onCambiar('numeroPersonas', Math.max(1, Number(evento.target.value)))}
        style={{ maxWidth: '140px' }}
      />

      <label htmlFor="distritoPartida" className="form-label fw-semibold">
        Distrito de partida
      </label>
      <select
        id="distritoPartida"
        className="form-select"
        value={formulario.distritoPartida}
        onChange={(evento) => onCambiar('distritoPartida', evento.target.value)}
      >
        <option value="">Selecciona un distrito</option>
        {DISTRITOS_LIMA.map((distrito) => (
          <option key={distrito} value={distrito}>
            {distrito}
          </option>
        ))}
      </select>
    </div>
  )
}

export default PasoTuViaje
