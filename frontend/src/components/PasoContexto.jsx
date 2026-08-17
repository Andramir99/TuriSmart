import { infoPresupuesto, infoGrupo } from '../utils/itinerarios.js'

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

      <div className="ts-resumen-perfil">
        <p className="fw-semibold mb-2">Resumen de tu perfil</p>
        <div className="d-flex flex-wrap gap-2">
          <span className="ts-badge-inline ts-badge--gastronomico">
            {formulario.duracionDias} días
          </span>
          <span className={presupuesto.clase}>{presupuesto.etiqueta}</span>
          <span className="ts-badge-inline ts-badge--natural">{grupo.etiqueta}</span>
        </div>
      </div>
    </div>
  )
}

export default PasoContexto
