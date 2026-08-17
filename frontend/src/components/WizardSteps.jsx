const PASOS = [
  { numero: 1, etiqueta: 'Tipo de viajero' },
  { numero: 2, etiqueta: 'Tu viaje' },
  { numero: 3, etiqueta: 'Contexto' },
]

// Indicador de progreso de 3 pasos, compartido por las 3 pantallas del
// wizard "Planifica tu viaje". Un paso ya completado muestra un check;
// el paso actual y los futuros muestran su número.
function WizardSteps({ pasoActual }) {
  const porcentaje = ((pasoActual - 1) / (PASOS.length - 1)) * 100

  return (
    <div className="ts-wizard-steps mb-4">
      <div className="d-flex justify-content-between mb-2">
        {PASOS.map((paso) => {
          const completado = paso.numero < pasoActual
          const activo = paso.numero === pasoActual
          return (
            <div
              key={paso.numero}
              className={`ts-wizard-step${activo ? ' ts-wizard-step--activo' : ''}${
                completado ? ' ts-wizard-step--completo' : ''
              }`}
            >
              <span className="ts-wizard-step-circle">
                {completado ? <i className="bi bi-check-lg"></i> : paso.numero}
              </span>
              <span className="ts-wizard-step-label">{paso.etiqueta}</span>
            </div>
          )
        })}
      </div>
      <div className="ts-wizard-steps-track">
        <div className="ts-wizard-steps-fill" style={{ width: `${porcentaje}%` }}></div>
      </div>
    </div>
  )
}

export default WizardSteps
