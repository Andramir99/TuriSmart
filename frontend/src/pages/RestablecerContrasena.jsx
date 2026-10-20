import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { ApiError } from '../services/api.js'
import { restablecerContrasena } from '../services/authService.js'
import CampoContrasena from '../components/CampoContrasena.jsx'
import '../styles/wizard.css'

function RestablecerContrasena() {
  const [parametros] = useSearchParams()
  const token = parametros.get('token') || ''
  const navigate = useNavigate()

  const [nuevaContrasena, setNuevaContrasena] = useState('')
  const [confirmacion, setConfirmacion] = useState('')
  const [error, setError] = useState('')
  const [enviando, setEnviando] = useState(false)
  const [listo, setListo] = useState(false)

  async function manejarSubmit(evento) {
    evento.preventDefault()
    setError('')

    if (nuevaContrasena !== confirmacion) {
      setError('Las contraseñas no coinciden.')
      return
    }

    setEnviando(true)
    try {
      await restablecerContrasena(token, nuevaContrasena)
      setListo(true)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo conectar con el servidor.')
    } finally {
      setEnviando(false)
    }
  }

  if (!token) {
    return (
      <div className="container py-5 text-center" style={{ maxWidth: '440px' }}>
        <div className="alert alert-danger">
          <i className="bi bi-exclamation-circle me-1"></i>
          Este enlace no es válido. Solicita uno nuevo desde la pantalla de inicio de sesión.
        </div>
        <Link to="/login" className="btn btn-ts-primary">
          Ir a iniciar sesión
        </Link>
      </div>
    )
  }

  return (
    <div className="container py-5" style={{ maxWidth: '440px' }}>
      <p className="ts-eyebrow mb-1">Cuenta</p>
      <h1 className="ts-heading mb-2">Elige tu nueva contraseña</h1>

      <div className="ts-wizard-card">
        {listo ? (
          <div>
            <div className="alert alert-success small py-2" role="status">
              <i className="bi bi-check-circle me-1"></i>
              Contraseña actualizada. Ya puedes iniciar sesión.
            </div>
            <button type="button" className="btn btn-ts-primary w-100" onClick={() => navigate('/login')}>
              Ir a iniciar sesión
            </button>
          </div>
        ) : (
          <form onSubmit={manejarSubmit} noValidate>
            <CampoContrasena
              id="nueva_contrasena"
              label="Nueva contraseña"
              value={nuevaContrasena}
              onChange={(evento) => setNuevaContrasena(evento.target.value)}
              minLength={8}
              autoComplete="new-password"
              helpText="Mínimo 8 caracteres."
            />
            <CampoContrasena
              id="confirmacion"
              label="Confirma la nueva contraseña"
              value={confirmacion}
              onChange={(evento) => setConfirmacion(evento.target.value)}
              minLength={8}
              autoComplete="new-password"
            />

            {error && (
              <div className="alert alert-danger small py-2" role="alert">
                <i className="bi bi-exclamation-circle me-1"></i>
                {error}
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
        )}
      </div>
    </div>
  )
}

export default RestablecerContrasena
