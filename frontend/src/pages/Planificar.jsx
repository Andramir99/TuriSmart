import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import WizardSteps from '../components/WizardSteps.jsx'
import PasoTipoViajero from '../components/PasoTipoViajero.jsx'
import PasoTuViaje from '../components/PasoTuViaje.jsx'
import PasoContexto from '../components/PasoContexto.jsx'
import RecomendacionCard from '../components/RecomendacionCard.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import { obtenerCategorias } from '../services/categoriasService.js'
import { enviarEncuesta } from '../services/encuestasService.js'
import { guardarPreferencias } from '../services/preferenciasService.js'
import { generarRecomendaciones } from '../services/recomendacionesService.js'
import { crearItinerario } from '../services/itinerariosService.js'
import {
  construirParadasDesdeRecomendaciones,
  calcularCantidadRecomendaciones,
} from '../utils/construirItinerario.js'
import { ApiError } from '../services/api.js'
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
  distritoPartida: '',
  distanciaMaximaKm: 10,
  horarioPreferido: 'cualquiera',
  movilidadReducida: false,
  idioma: 'es',
  fechaInicio: '',
  consentimientoDatos: false,
}

function Planificar() {
  const { token, autenticado } = useAuth()
  const [paso, setPaso] = useState(1)
  const [formulario, setFormulario] = useState(FORMULARIO_INICIAL)
  const [enviando, setEnviando] = useState(false)
  const [errorEnvio, setErrorEnvio] = useState('')
  const [completado, setCompletado] = useState(false)
  const [recomendaciones, setRecomendaciones] = useState([])
  const [errorRecomendaciones, setErrorRecomendaciones] = useState('')
  const [itinerarioCreado, setItinerarioCreado] = useState(null)
  const [errorItinerario, setErrorItinerario] = useState('')

  const [categorias, setCategorias] = useState([])
  const [cargandoCategorias, setCargandoCategorias] = useState(true)
  const [errorCategorias, setErrorCategorias] = useState('')

  useEffect(() => {
    cargarCategorias()
  }, [])

  function cargarCategorias() {
    setCargandoCategorias(true)
    setErrorCategorias('')
    obtenerCategorias()
      .then(setCategorias)
      .catch((err) => {
        setErrorCategorias(
          err instanceof ApiError ? err.message : 'No se pudieron cargar las categorías.',
        )
      })
      .finally(() => setCargandoCategorias(false))
  }

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

  // Validaciones mínimas por paso: no avanzar del 1 sin elegir interés,
  // no poder enviar el 3 sin dar el consentimiento de datos.
  const puedeAvanzar = paso !== 1 || formulario.tiposViajero.length > 0
  const puedeEnviar = formulario.consentimientoDatos

  function irSiguiente() {
    if (paso < 3) setPaso(paso + 1)
  }

  function irAnterior() {
    if (paso > 1) setPaso(paso - 1)
  }

  async function generarItinerario() {
    setErrorEnvio('')
    setEnviando(true)
    try {
      const respuestas = {
        categorias_interes: formulario.tiposViajero.join(','),
        duracion_dias: String(formulario.duracionDias),
        presupuesto: formulario.presupuesto,
        tipo_compania: formulario.tipoGrupo,
        distrito_partida: formulario.distritoPartida,
        distancia_maxima_km: String(formulario.distanciaMaximaKm),
        horario_preferido: formulario.horarioPreferido,
        movilidad_reducida: String(formulario.movilidadReducida),
        idioma_preferido: formulario.idioma,
        fecha_inicio: formulario.fechaInicio,
      }

      await enviarEncuesta(
        { consentimiento_datos: formulario.consentimientoDatos, respuestas },
        token,
      )

      // Si hay sesión iniciada, además dejamos sus preferencias guardadas
      // en el perfil (Etapa 8: "posibilidad de modificar las preferencias").
      if (autenticado) {
        await guardarPreferencias(
          {
            presupuesto: formulario.presupuesto,
            tipo_viaje: formulario.tipoGrupo,
            tiempo_disponible_dias: formulario.duracionDias,
            distrito_partida: formulario.distritoPartida || null,
            distancia_maxima_km: formulario.distanciaMaximaKm,
            categorias: formulario.tiposViajero,
          },
          token,
        )
      }

      setCompletado(true)

      // Las recomendaciones se piden aparte y con su propio manejo de
      // error: si fallan, la encuesta ya quedó guardada de todas formas,
      // así que no tiene sentido bloquear la pantalla de éxito por esto.
      try {
        const resultado = await generarRecomendaciones(
          {
            categorias: formulario.tiposViajero,
            presupuesto: formulario.presupuesto,
            distrito_partida: formulario.distritoPartida || null,
            distancia_maxima_km: formulario.distanciaMaximaKm,
            cantidad: calcularCantidadRecomendaciones(formulario.duracionDias),
          },
          token,
        )
        setRecomendaciones(resultado)

        // Solo con sesión iniciada tiene sentido guardar un itinerario:
        // "Mis Itinerarios" es una lista ligada a la cuenta (Etapa 10).
        // Para alguien anónimo, las tarjetas de recomendación de arriba
        // ya cumplen la promesa de la Home ("sin registro previo").
        if (autenticado) {
          try {
            const paradas = construirParadasDesdeRecomendaciones(resultado, formulario.duracionDias)
            const nuevoItinerario = await crearItinerario(
              {
                titulo: `Lima a tu medida — ${formulario.duracionDias} día${formulario.duracionDias === 1 ? '' : 's'}`,
                fecha_inicio: formulario.fechaInicio || null,
                presupuesto: formulario.presupuesto,
                tipo_grupo: formulario.tipoGrupo,
                recomendacion_ia:
                  'Itinerario armado automáticamente a partir de tus 5 mejores recomendaciones.',
                paradas,
              },
              token,
            )
            setItinerarioCreado(nuevoItinerario)
          } catch (err) {
            setErrorItinerario(
              err instanceof ApiError ? err.message : 'No se pudo guardar el itinerario.',
            )
          }
        }
      } catch (err) {
        setErrorRecomendaciones(
          err instanceof ApiError ? err.message : 'No se pudieron calcular las recomendaciones.',
        )
      }
    } catch (err) {
      setErrorEnvio(
        err instanceof ApiError ? err.message : 'No se pudo guardar la encuesta. Intenta de nuevo.',
      )
    } finally {
      setEnviando(false)
    }
  }

  if (completado) {
    return (
      <div className="container py-5 text-center">
        <p className="ts-eyebrow mb-2">¡Listo!</p>
        <h1 className="ts-heading mb-3">
          <i className="bi bi-check-circle-fill text-success me-2"></i>
          Encuesta registrada
        </h1>
        <p className="text-muted mb-4 mx-auto" style={{ maxWidth: '560px' }}>
          Guardamos tus preferencias{autenticado ? ' en tu cuenta' : ' de forma anónima'}. Estas
          son las {recomendaciones.length || calcularCantidadRecomendaciones(formulario.duracionDias)}{' '}
          mejores coincidencias para tu viaje de {formulario.duracionDias} día
          {formulario.duracionDias === 1 ? '' : 's'}, según el recomendador inicial de TuriSmart
          (basado en reglas de contenido, no todavía en Machine Learning entrenado)
          {autenticado ? ', ya repartidas en un itinerario guardado en tu cuenta.' : '.'}
        </p>

        {errorRecomendaciones ? (
          <div className="alert alert-danger d-inline-block mb-4">
            <i className="bi bi-exclamation-circle me-1"></i> {errorRecomendaciones}
          </div>
        ) : recomendaciones.length === 0 ? (
          <div className="text-muted mb-4">
            <span className="spinner-border spinner-border-sm me-2"></span>
            Calculando recomendaciones...
          </div>
        ) : (
          <div className="row g-4 text-start mb-4">
            {recomendaciones.map((recomendacion) => (
              <div className="col-6 col-lg-3" key={recomendacion.lugar.id}>
                <RecomendacionCard recomendacion={recomendacion} />
              </div>
            ))}
          </div>
        )}

        {autenticado && errorItinerario && (
          <div className="alert alert-warning d-inline-block mb-4">
            <i className="bi bi-exclamation-triangle me-1"></i> {errorItinerario}
          </div>
        )}

        <div className="d-flex justify-content-center gap-3 flex-wrap">
          {itinerarioCreado && (
            <Link to={`/itinerario/${itinerarioCreado.id}`} className="btn btn-ts-primary rounded-pill px-4">
              <i className="bi bi-map me-1"></i> Ver mi itinerario
            </Link>
          )}
          <Link
            to="/explorar"
            className={`btn rounded-pill px-4 ${itinerarioCreado ? 'btn-light border' : 'btn-ts-primary'}`}
          >
            Explorar más destinos
          </Link>
          {!autenticado && (
            <Link to="/login" className="btn btn-light border rounded-pill px-4">
              Crear cuenta para guardar itinerarios
            </Link>
          )}
        </div>
      </div>
    )
  }

  const { eyebrow, titulo, descripcion } = TITULOS_PASO[paso]

  return (
    <div className="container py-5" style={{ maxWidth: '840px' }}>
      <WizardSteps pasoActual={paso} />

      <div className="ts-wizard-card">
        <p className="ts-eyebrow mb-1">{eyebrow}</p>
        <h1 className="h3 ts-heading mb-2">{titulo}</h1>
        <p className="text-muted mb-4">{descripcion}</p>

        {paso === 1 &&
          (cargandoCategorias ? (
            <div className="text-center text-muted py-4">
              <span className="spinner-border spinner-border-sm me-2"></span>
              Cargando categorías...
            </div>
          ) : errorCategorias ? (
            <div className="alert alert-danger d-flex justify-content-between align-items-center">
              <span>
                <i className="bi bi-exclamation-circle me-1"></i> {errorCategorias}
              </span>
              <button type="button" className="btn btn-sm btn-outline-danger" onClick={cargarCategorias}>
                Reintentar
              </button>
            </div>
          ) : (
            <PasoTipoViajero
              opciones={categorias}
              seleccionados={formulario.tiposViajero}
              onAlternar={alternarTipoViajero}
            />
          ))}

        {paso === 2 && <PasoTuViaje formulario={formulario} onCambiar={actualizarCampo} />}

        {paso === 3 && <PasoContexto formulario={formulario} onCambiar={actualizarCampo} />}

        {errorEnvio && (
          <div className="alert alert-danger small mt-3 mb-0" role="alert">
            <i className="bi bi-exclamation-circle me-1"></i>
            {errorEnvio}
          </div>
        )}

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
              disabled={enviando || !puedeEnviar}
            >
              {enviando ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                  Guardando...
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
        {paso === 3 && !puedeEnviar && (
          <p className="text-danger small mt-3 mb-0">
            <i className="bi bi-exclamation-circle me-1"></i>
            Marca la casilla de consentimiento para poder continuar.
          </p>
        )}
      </div>
    </div>
  )
}

export default Planificar
