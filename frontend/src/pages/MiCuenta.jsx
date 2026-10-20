import { useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { ApiError } from '../services/api.js'
import { cambiarContrasena } from '../services/authService.js'
import CampoContrasena from '../components/CampoContrasena.jsx'
import '../styles/wizard.css'

const FORM_VACIO = { actual: '', nueva: '', confirmacion: '' }

function MiCuenta() {
  const { usuario, token } = useAuth()
  const [form, setForm] = useState(FORM_VACIO)
  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')
  const [enviando, setEnviando] = useState(false)

  function actualizarCampo(campo, valor) {
    setForm((actual) => ({ ...actual, [campo]: valor }))
  }

  async function manejarSubmit(evento) {
    evento.preventDefault()
    setError('')
    setMensaje('')

    if (form.nueva !== form.confirmacion) {
      setError('La nueva contraseña y su confirmación no coinciden.')
      return
    }

    setEnviando(true)
    try {
      const respuesta = await cambiarContrasena(form.actual, form.nueva, token)
      setMensaje(respuesta.mensaje)
      setForm(FORM_VACIO)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo conectar con el servidor.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="container py-5" style={{ maxWidth: '440px' }}>
      <p className="ts-eyebrow mb-1">Mi cuenta</p>
      <h1 className="ts-heading mb-2">Hola, {usuario.nombre.split(' ')[0]}</h1>
      <p className="text-muted mb-4">{usuario.correo}</p>

      <div className="ts-wizard-card">
        <h2 className="h5 fw-bold mb-3">Cambiar contraseña</h2>

        <form onSubmit={manejarSubmit} noValidate>
          <CampoContrasena
            id="contrasena_actual"
            label="Contraseña actual"
            value={form.actual}
            onChange={(evento) => actualizarCampo('actual', evento.target.value)}
            autoComplete="current-password"
          />
          <CampoContrasena
            id="nueva_contrasena"
            label="Nueva contraseña"
            value={form.nueva}
            onChange={(evento) => actualizarCampo('nueva', evento.target.value)}
            minLength={8}
            autoComplete="new-password"
            helpText="Mínimo 8 caracteres."
          />
          <CampoContrasena
            id="confirmacion_contrasena"
            label="Confirma la nueva contraseña"
            value={form.confirmacion}
            onChange={(evento) => actualizarCampo('confirmacion', evento.target.value)}
            minLength={8}
            autoComplete="new-password"
          />

          {error && (
            <div className="alert alert-danger small py-2" role="alert">
              <i className="bi bi-exclamation-circle me-1"></i>
              {error}
            </div>
          )}
          {mensaje && (
            <div className="alert alert-success small py-2" role="status">
              <i className="bi bi-check-circle me-1"></i>
              {mensaje}
            </div>
          )}

          <button type="submit" className="btn btn-ts-primary w-100" disabled={enviando}>
            {enviando ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                Guardando...
              </>
            ) : (
              'Guardar nueva contraseña'
            )}
          </button>
        </form>
      </div>
    </div>
  )
}

export default MiCuenta
