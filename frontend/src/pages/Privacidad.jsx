import { useState } from 'react'
import { enviarSolicitudArco } from '../services/solicitudesArcoService.js'
import { ApiError } from '../services/api.js'
import '../styles/wizard.css'

const TIPOS_SOLICITUD = [
  { slug: 'acceso', etiqueta: 'Acceso', descripcion: 'Quiero conocer qué información mía tienen guardada.' },
  { slug: 'rectificacion', etiqueta: 'Rectificación', descripcion: 'Un dato mío (nombre, correo) está mal registrado.' },
  { slug: 'cancelacion', etiqueta: 'Cancelación', descripcion: 'Quiero que eliminen mi cuenta y mis datos.' },
  { slug: 'oposicion', etiqueta: 'Oposición', descripcion: 'No quiero que sigan usando mi información.' },
]

const FORMULARIO_INICIAL = { nombre: '', correo: '', tipo_solicitud: '', mensaje: '' }

function Privacidad() {
  const [formulario, setFormulario] = useState(FORMULARIO_INICIAL)
  const [enviando, setEnviando] = useState(false)
  const [error, setError] = useState('')
  const [enviado, setEnviado] = useState(false)

  function actualizarCampo(campo, valor) {
    setFormulario((actual) => ({ ...actual, [campo]: valor }))
  }

  async function manejarSubmit(evento) {
    evento.preventDefault()
    setError('')
    setEnviando(true)
    try {
      await enviarSolicitudArco(formulario)
      setEnviado(true)
      setFormulario(FORMULARIO_INICIAL)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo enviar tu solicitud. Intenta de nuevo.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="container py-5" style={{ maxWidth: '720px' }}>
      <p className="ts-eyebrow mb-1">Tus datos</p>
      <h1 className="ts-heading mb-3">Privacidad y protección de datos</h1>

      <p className="text-muted">
        En TuriSmart Lima tratamos tu información conforme a la Ley N.° 29733, Ley de Protección de
        Datos Personales. No pedimos datos sensibles (DNI, salud, etc.). Las contraseñas se guardan
        encriptadas (bcrypt) y nunca en texto plano. Las respuestas de la encuesta de planificación
        se guardan de forma seudonimizada: no quedan vinculadas directamente a tu nombre o correo,
        solo se usan para mejorar el motor de recomendación.
      </p>

      <h2 className="h5 mt-4 mb-2">Tus derechos sobre tu información (Derechos ARCO)</h2>
      <p className="text-muted">
        Puedes pedirnos en cualquier momento que <strong>accedas</strong> a tus datos, los{' '}
        <strong>rectifiques</strong>, los <strong>canceles</strong> (eliminar tu cuenta) u{' '}
        <strong>oponerte</strong> a que sigamos usándolos. Hoy este proceso se atiende de forma manual:
        completa el formulario y un miembro del equipo te responderá al correo indicado.
      </p>

      {enviado ? (
        <div className="alert alert-success mt-4">
          <i className="bi bi-check-circle-fill me-2"></i>
          Recibimos tu solicitud. Te responderemos al correo que dejaste en los próximos días.
        </div>
      ) : (
        <form onSubmit={manejarSubmit} noValidate className="ts-wizard-card mt-4">
          <div className="mb-3">
            <label htmlFor="nombre" className="form-label fw-semibold">
              Nombre
            </label>
            <input
              id="nombre"
              type="text"
              className="form-control"
              value={formulario.nombre}
              onChange={(evento) => actualizarCampo('nombre', evento.target.value)}
              required
              minLength={2}
            />
          </div>

          <div className="mb-3">
            <label htmlFor="correo" className="form-label fw-semibold">
              Correo de contacto
            </label>
            <input
              id="correo"
              type="email"
              className="form-control"
              value={formulario.correo}
              onChange={(evento) => actualizarCampo('correo', evento.target.value)}
              required
            />
          </div>

          <p className="form-label fw-semibold mb-2">¿Qué derecho quieres ejercer?</p>
          <div className="row g-2 mb-3">
            {TIPOS_SOLICITUD.map((opcion) => (
              <div className="col-6" key={opcion.slug}>
                <button
                  type="button"
                  className={`ts-opcion-boton w-100 text-start${
                    formulario.tipo_solicitud === opcion.slug ? ' ts-opcion-boton--activo' : ''
                  }`}
                  onClick={() => actualizarCampo('tipo_solicitud', opcion.slug)}
                  aria-pressed={formulario.tipo_solicitud === opcion.slug}
                >
                  <span className="d-block fw-semibold">{opcion.etiqueta}</span>
                  <span className="d-block small text-muted">{opcion.descripcion}</span>
                </button>
              </div>
            ))}
          </div>

          <div className="mb-3">
            <label htmlFor="mensaje" className="form-label fw-semibold">
              Cuéntanos con más detalle qué necesitas
            </label>
            <textarea
              id="mensaje"
              className="form-control"
              rows={4}
              value={formulario.mensaje}
              onChange={(evento) => actualizarCampo('mensaje', evento.target.value)}
              required
              minLength={5}
            />
          </div>

          {error && (
            <div className="alert alert-danger small py-2" role="alert">
              <i className="bi bi-exclamation-circle me-1"></i>
              {error}
            </div>
          )}

          <button
            type="submit"
            className="btn btn-ts-primary w-100"
            disabled={enviando || !formulario.tipo_solicitud}
          >
            {enviando ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                Enviando...
              </>
            ) : (
              'Enviar solicitud'
            )}
          </button>
        </form>
      )}
    </div>
  )
}

export default Privacidad
