import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { ApiError } from '../services/api.js'
import '../styles/wizard.css'

function Login() {
  const { iniciarSesion, registrar } = useAuth()
  const navigate = useNavigate()
  const ubicacion = useLocation()
  // Si RutaPrivada nos mandó para acá (por ejemplo, alguien sin sesión
  // intentó entrar a /itinerario), al iniciar sesión lo regresamos ahí
  // en vez de siempre mandarlo al inicio.
  const destino = ubicacion.state?.desde || '/'

  const [modo, setModo] = useState('login') // 'login' | 'registro'
  const [form, setForm] = useState({ nombre: '', correo: '', contrasena: '' })
  const [error, setError] = useState('')
  const [enviando, setEnviando] = useState(false)

  function actualizarCampo(campo, valor) {
    setForm((actual) => ({ ...actual, [campo]: valor }))
  }

  function cambiarModo(nuevoModo) {
    setModo(nuevoModo)
    setError('')
  }

  async function manejarSubmit(evento) {
    evento.preventDefault()
    setError('')
    setEnviando(true)
    try {
      if (modo === 'login') {
        await iniciarSesion(form.correo, form.contrasena)
      } else {
        await registrar(form.nombre, form.correo, form.contrasena)
      }
      navigate(destino, { replace: true })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo conectar con el servidor.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="container py-5" style={{ maxWidth: '440px' }}>
      <p className="ts-eyebrow mb-1">Cuenta</p>
      <h1 className="ts-heading mb-2">{modo === 'login' ? 'Iniciar sesión' : 'Crear cuenta'}</h1>
      <p className="text-muted mb-4">
        {modo === 'login'
          ? 'Ingresa para ver y guardar tus itinerarios.'
          : 'Regístrate para guardar tus itinerarios y valorar lugares.'}
      </p>

      <div className="ts-wizard-card">
        <form onSubmit={manejarSubmit} noValidate>
          {modo === 'registro' && (
            <div className="mb-3">
              <label htmlFor="nombre" className="form-label fw-semibold">
                Nombre
              </label>
              <input
                id="nombre"
                type="text"
                className="form-control"
                value={form.nombre}
                onChange={(evento) => actualizarCampo('nombre', evento.target.value)}
                required
                minLength={2}
                autoComplete="name"
              />
            </div>
          )}

          <div className="mb-3">
            <label htmlFor="correo" className="form-label fw-semibold">
              Correo
            </label>
            <input
              id="correo"
              type="email"
              className="form-control"
              value={form.correo}
              onChange={(evento) => actualizarCampo('correo', evento.target.value)}
              required
              autoComplete="email"
            />
          </div>

          <div className="mb-3">
            <label htmlFor="contrasena" className="form-label fw-semibold">
              Contraseña
            </label>
            <input
              id="contrasena"
              type="password"
              className="form-control"
              value={form.contrasena}
              onChange={(evento) => actualizarCampo('contrasena', evento.target.value)}
              required
              minLength={8}
              autoComplete={modo === 'login' ? 'current-password' : 'new-password'}
            />
            {modo === 'registro' && <div className="form-text">Mínimo 8 caracteres.</div>}
          </div>

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
                {modo === 'login' ? 'Ingresando...' : 'Creando cuenta...'}
              </>
            ) : modo === 'login' ? (
              'Ingresar'
            ) : (
              'Crear cuenta'
            )}
          </button>
        </form>

        <p className="text-center small text-muted mt-3 mb-0">
          {modo === 'login' ? (
            <>
              ¿No tienes cuenta?{' '}
              <button
                type="button"
                className="btn btn-link p-0 align-baseline"
                onClick={() => cambiarModo('registro')}
              >
                Regístrate
              </button>
            </>
          ) : (
            <>
              ¿Ya tienes cuenta?{' '}
              <button
                type="button"
                className="btn btn-link p-0 align-baseline"
                onClick={() => cambiarModo('login')}
              >
                Inicia sesión
              </button>
            </>
          )}
        </p>
      </div>
    </div>
  )
}

export default Login
