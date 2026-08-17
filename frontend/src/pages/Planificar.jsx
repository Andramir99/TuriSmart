import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import WizardSteps from '../components/WizardSteps.jsx'
import PasoTipoViajero from '../components/PasoTipoViajero.jsx'
import PasoTuViaje from '../components/PasoTuViaje.jsx'
import PasoContexto from '../components/PasoContexto.jsx'
import '../styles/wizard.css'

const TITULOS_PASO = {
  1: { eyebrow: 'Paso 1 de 3', titulo: '¿Qué tipo de viajero eres?', descripcion: 'Selecciona todas las que apliquen. Usaremos esto para personalizar tu ruta.' },
  2: { eyebrow: 'Paso 2 de 3', titulo: 'Cuéntanos sobre tu viaje', descripcion: 'Personalizamos cada recomendación según tu disponibilidad y presupuesto.' },
  3: { eyebrow: 'Paso 3 de 3', titulo: 'Contexto adicional', descripcion: 'Últimos detalles para afinar tu itinerario perfecto.' },
}

const FORMULARIO_INICIAL = {
  tiposViajero: [],
  duracionDias: 3,
  presupuesto: 'moderado',
  tipoGrupo: 'pareja',
  movilidadReducida: false,
  idioma: 'es',
  fechaInicio: '',
}

function Planificar() {
  const navigate = useNavigate()
  const [paso, setPaso] = useState(1)
  const [formulario, setFormulario] = useState(FORMULARIO_INICIAL)
  const [generando, setGenerando] = useState(false)

  function actualizarCampo(campo, valor) {
    setFormulario((actual) => ({ ...actual, [campo]: valor }))
  }

  function alternarTipoViajero(slug) {
    setFormulario((actual) => {
      const yaEstaba = actual.tiposViajero.includes(slug)
      return {
        ...actual,
        tiposViajero: yaEstaba
          ? actual.tiposViajero.filter((item) => item !== slug)
          : [...actual.tiposViajero, slug],
      }
    })
  }

  // Validación mínima: en el Paso 1 hace falta elegir al menos un interés
  // para poder avanzar. Etapas futuras (8-9) sumarán más validaciones
  // cuando esta encuesta se conecte con el backend real.
  const puedeAvanzar = paso !== 1 || formulario.tiposViajero.length > 0

  function irSiguiente() {
    if (paso < 3) setPaso(paso + 1)
  }

  function irAnterior() {
    if (paso > 1) setPaso(paso - 1)
  }

  function generarItinerario() {
    setGenerando(true)
    // Simulación de "estado de carga" mientras no existe backend todavía.
    // En la Etapa 8-9 esto se reemplaza por POST /encuestas + POST /recomendaciones.
    setTimeout(() => {
      navigate('/itinerario')
    }, 900)
  }

  const { eyebrow, titulo, descripcion } = TITULOS_PASO[paso]

  return (
    <div className="container py-5" style={{ maxWidth: '840px' }}>
      <WizardSteps pasoActual={paso} />

      <div className="ts-wizard-card">
        <p className="ts-eyebrow mb-1">{eyebrow}</p>
        <h1 className="h3 ts-heading mb-2">{titulo}</h1>
        <p className="text-muted mb-4">{descripcion}</p>

        {paso === 1 && (
          <PasoTipoViajero
            seleccionados={formulario.tiposViajero}
            onAlternar={alternarTipoViajero}
          />
        )}

        {paso === 2 && <PasoTuViaje formulario={formulario} onCambiar={actualizarCampo} />}

        {paso === 3 && <PasoContexto formulario={formulario} onCambiar={actualizarCampo} />}

        <div className="d-flex justify-content-between align-items-center mt-4">
          <button
            type="button"
            className="btn btn-light border"
            onClick={irAnterior}
            disabled={paso === 1}
          >
            <i className="bi bi-chevron-left me-1"></i> Anterior
          </button>

          {paso < 3 ? (
            <button
              type="button"
              className="btn btn-ts-primary"
              onClick={irSiguiente}
              disabled={!puedeAvanzar}
            >
              Siguiente <i className="bi bi-chevron-right ms-1"></i>
            </button>
          ) : (
            <button
              type="button"
              className="btn btn-ts-primary rounded-pill px-4"
              onClick={generarItinerario}
              disabled={generando}
            >
              {generando ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                  Generando...
                </>
              ) : (
                <>
                  <i className="bi bi-stars me-1"></i> Generar mi itinerario con IA
                </>
              )}
            </button>
          )}
        </div>

        {paso === 1 && !puedeAvanzar && (
          <p className="text-danger small mt-3 mb-0">
            <i className="bi bi-exclamation-circle me-1"></i>
            Elige al menos un tipo de viajero para continuar.
          </p>
        )}
      </div>
    </div>
  )
}

export default Planificar
