import { infoPresupuesto, infoGrupo } from '../utils/itinerarios.js'

const HORARIOS = [
  { slug: 'manana', etiqueta: 'Mañana' },
  { slug: 'tarde', etiqueta: 'Tarde' },
  { slug: 'noche', etiqueta: 'Noche' },
  { slug: 'cualquiera', etiqueta: 'Cualquiera' },
]

function PasoContexto({ formulario, onCambiar }) {
  const presupuesto = infoPresupuesto(formulario.presupuesto)
  const grupo = infoGrupo(formulario.tipoGrupo)

  return (
    <div>
      <div className="ts-toggle-row mb-4">
        <div>
          <p className="fw-semibold mb-1">¿Tienes movilidad reducida?</p>
          <p className="small text-muted mb-0">
            Filtramos destinos accesibles para silla de ruedas
          </p>
        </div>
        <div className="form-check form-switch">
          <input
            className="form-check-input"
            type="checkbox"
            role="switch"
            id="movilidadReducida"
            checked={formulario.movilidadReducida}
            onChange={(evento) => onCambiar('movilidadReducida', evento.target.checked)}
          />
        </div>
      </div>

      <div className="mb-4">
        <label htmlFor="idioma" className="form-label fw-semibold">
          Idioma preferido
        </label>
        <select
          id="idioma"
          className="form-select"
          value={formulario.idioma}
          onChange={(evento) => onCambiar('idioma', evento.target.value)}
        >
          <option value="es">Español</option>
          <option value="en">English</option>
          <option value="pt">Português</option>
          <option value="fr">Français</option>
        </select>
      </div>

      <div className="mb-4">
        <label htmlFor="fechaInicio" className="form-label fw-semibold">
          Fecha de inicio del viaje
        </label>
        <input
          id="fechaInicio"
          type="date"
          className="form-control"
          value={formulario.fechaInicio}
          onChange={(evento) => onCambiar('fechaInicio', evento.target.value)}
        />
      </div>

      <label htmlFor="distanciaMaxima" className="form-label fw-semibold">
        Distancia máxima que deseas recorrer:{' '}
        <span className="ts-text-primary">{formulario.distanciaMaximaKm} km</span>
      </label>
      <input
        id="distanciaMaxima"
        type="range"
        className="form-range mb-1"
        min={1}
        max={30}
        value={formulario.distanciaMaximaKm}
        onChange={(evento) => onCambiar('distanciaMaximaKm', Number(evento.target.value))}
      />
      <div className="d-flex justify-content-between small text-muted mb-4">
        <span>1 km</span>
        <span>30 km</span>
      </div>

      <p className="form-label fw-semibold mb-2">Horario preferido</p>
      <div className="row g-2 mb-4">
        {HORARIOS.map((opcion) => (
          <div className="col-6 col-md-3" key={opcion.slug}>
            <button
              type="button"
              className={`ts-opcion-boton w-100${
                formulario.horarioPreferido === opcion.slug ? ' ts-opcion-boton--activo' : ''
              }`}
              onClick={() => onCambiar('horarioPreferido', opcion.slug)}
              aria-pressed={formulario.horarioPreferido === opcion.slug}
            >
              {opcion.etiqueta}
            </button>
          </div>
        ))}
      </div>

      <div className="ts-resumen-perfil mb-4">
        <p className="fw-semibold mb-2">Resumen de tu perfil</p>
        <div className="d-flex flex-wrap gap-2">
          <span className="ts-badge-inline ts-badge--gastronomico">
            {formulario.duracionDias} días
          </span>
          <span className={presupuesto.clase}>{presupuesto.etiqueta}</span>
          <span className="ts-badge-inline ts-badge--natural">{grupo.etiqueta}</span>
        </div>
      </div>

      <div className="form-check">
        <input
          className="form-check-input"
          type="checkbox"
          id="consentimientoDatos"
          checked={formulario.consentimientoDatos}
          onChange={(evento) => onCambiar('consentimientoDatos', evento.target.checked)}
        />
        <label className="form-check-label small" htmlFor="consentimientoDatos">
          Acepto que mis respuestas se usen de forma anonimizada con fines académicos, para
          mejorar las recomendaciones de TuriSmart Lima.
        </label>
      </div>
    </div>
  )
}

export default PasoContexto
