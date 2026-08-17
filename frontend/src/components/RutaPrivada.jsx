import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

// Envuelve una <Route element={...}> para exigir sesión iniciada.
// Mientras se confirma el token guardado (cargando), no redirige todavía
// — evita mandar a alguien ya logueado a /login solo porque la
// verificación no había terminado.
function RutaPrivada({ children }) {
  const { autenticado, cargando } = useAuth()
  const ubicacion = useLocation()

  if (cargando) {
    return (
      <div className="container py-5 text-center text-muted">
        <span className="spinner-border spinner-border-sm me-2"></span>
        Verificando sesión...
      </div>
    )
  }

  if (!autenticado) {
    return <Navigate to="/login" state={{ desde: ubicacion.pathname }} replace />
  }

  return children
}

export default RutaPrivada
