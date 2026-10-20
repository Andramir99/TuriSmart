import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { ApiError } from '../services/api.js'
import { solicitarRestablecimiento } from '../services/authService.js'
import CampoContrasena from '../components/CampoContrasena.jsx'
import '../styles/wizard.css'

const TITULOS = {
  login: 'Iniciar sesión',
  registro: 'Crear cuenta',
  olvide: 'Restablecer contraseña',
}

function Login() {
  const { iniciarSesion, registrar } = useAuth()
  const navigate = useNavigate()
  const ubicacion = useLocation()
  // Si RutaPrivada nos mandó para acá (por ejemplo, alguien sin sesión
  // intentó entrar a /itinerario), al iniciar sesión lo regresamos ahí
  // en vez de siempre mandarlo al inicio.
  const destino = ubicacion.state?.desde || '/'

  const [modo, setModo] = useState('login') // 'login' | 'registro' | 'olvide'
  const [form, setForm] = useState({ nombre: '', correo: '', contrasena: '' })
  const [error, setError] = useState('')
  const [enviando, setEnviando] = useState(false)

  // Resultado de pedir el restablecimiento: como el proyecto no tiene un
  // servidor de correo configurado (ver README), el backend devuelve el
  // enlace directo en la respuesta en vez de mandarlo por email — modo
  // prototipo, documentado como limitación conocida.
  const [resultadoOlvide, setResultadoOlvide] = useState(null)

  function actualizarCampo(campo, valor) {
    setForm((actual) => ({ ...actual, [campo]: valor }))
  }

  function cambiarModo(nuevoModo) {
    setModo(nuevoModo)
    setError('')
    setResultadoOlvide(null)
  }

  async function manejarSubmit(evento) {
    evento.preventDefault()
    setError('')
    setEnviando(true)
    try {
      if (modo === 'login') {
        await iniciarSesion(form.correo, form.contrasena)
        navigate(destino, { replace: true })
      } else if (modo === 'registro') {
        await registrar(form.nombre, form.correo, form.contrasena)
        navigate(destino, { replace: true })
      } else {
        const respuesta = await solicitarRestablecimiento(form.correo)
        setResultadoOlvide(respuesta)
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo conectar con el servidor.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="container py-5" style={{ maxWidth: '440px' }}>
      <p className="ts-eyebrow mb-1">Cuenta</p>
      <h1 className="ts-heading mb-2">{TITULOS[modo]}</h1>
      <p className="text-muted mb-4">
        {modo === 'login' && 'Ingresa para ver y guardar tus itinerarios.'}
        {modo === 'registro' && 'Regístrate para guardar tus itinerarios y valorar lugares.'}
        {modo === 'olvide' && 'Ingresa tu correo y te mostramos cómo continuar.'}
      </p>

      <div className="ts-wizard-card">
        {modo === 'olvide' && resultadoOlvide ? (
          <div>
            <div className="alert alert-success small py-2" role="status">
              <i className="bi bi-check-circle me-1"></i>
              {resultadoOlvide.mensaje}
            </div>
            {resultadoOlvide.token && (
              <>
                <p className="small text-muted mb-2">
                  Como este es un prototipo sin envío real de correos, aquí tienes tu enlace (vence en 30
                  minutos):
                </p>
                <Link
                  to={`/restablecer-contrasena?token=${encodeURIComponent(resultadoOlvide.token)}`}
                  className="btn btn-ts-primary w-100"
                >
                  Continuar con el restablecimiento
                </Link>
              </>
            )}
            <p className="text-center small text-muted mt-3 mb-0">
              <button type="button" className="btn btn-link p-0 align-baseline" onClick={() => cambiarModo('login')}>
                Volver a iniciar sesión
              </button>
            </p>
          </div>
        ) : (
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

            {modo !== 'olvide' && (
              <CampoContrasena
                id="contrasena"
                label="Contraseña"
                value={form.contrasena}
                onChange={(evento) => actualizarCampo('contrasena', evento.target.value)}
                minLength={modo === 'registro' ? 8 : undefined}
                autoComplete={modo === 'login' ? 'current-password' : 'new-password'}
                helpText={modo === 'registro' ? 'Mínimo 8 caracteres.' : null}
              />
            )}

            {modo === 'login' && (
              <p className="text-end mb-3">
                <button
                  type="button"
                  className="btn btn-link p-0 small align-baseline"
                  onClick={() => cambiarModo('olvide')}
                >
                  ¿Olvidaste tu contraseña?
                </button>
              </p>
            )}

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
                  {modo === 'login' && 'Ingresando...'}
                  {modo === 'registro' && 'Creando cuenta...'}
                  {modo === 'olvide' && 'Enviando...'}
                </>
              ) : (
                <>
                  {modo === 'login' && 'Ingresar'}
                  {modo === 'registro' && 'Crear cuenta'}
                  {modo === 'olvide' && 'Continuar'}
                </>
              )}
            </button>
          </form>
        )}

        {!resultadoOlvide && (
          <p className="text-center small text-muted mt-3 mb-0">
            {modo === 'login' && (
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
            )}
            {modo === 'registro' && (
              <>
                ¿Ya tienes cuenta?{' '}
                <button type="button" className="btn btn-link p-0 align-baseline" onClick={() => cambiarModo('login')}>
                  Inicia sesión
                </button>
              </>
            )}
            {modo === 'olvide' && (
              <button type="button" className="btn btn-link p-0 align-baseline" onClick={() => cambiarModo('login')}>
                Volver a iniciar sesión
              </button>
            )}
          </p>
        )}
      </div>
    </div>
  )
}

export default Login
