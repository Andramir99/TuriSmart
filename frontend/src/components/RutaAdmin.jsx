import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

// Igual que RutaPrivada, pero además exige rol "admin". Un usuario con
// sesión iniciada pero sin ese rol no ve el panel: se le manda al inicio
// en vez de a /login (ya está autenticado, solo no tiene permiso).
function RutaAdmin({ children }) {
  const { autenticado, usuario, cargando } = useAuth()
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

  if (usuario?.rol !== 'admin') {
    return <Navigate to="/" replace />
  }

  return children
}

export default RutaAdmin
