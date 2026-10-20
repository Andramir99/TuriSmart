import { useEffect, useState } from 'react'
import StatCard from '../components/StatCard.jsx'
import LineChartTendencia from '../components/LineChartTendencia.jsx'
import BarChartCategorias from '../components/BarChartCategorias.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import { obtenerPanelAdmin } from '../services/analiticaService.js'
import { ApiError } from '../services/api.js'
import '../styles/dashboard.css'

function construirTarjetas(m) {
  return [
    {
      id: 'usuarios',
      icono: 'bi-people-fill',
      colorIcono: '#3355cc',
      fondoIcono: '#e8eefc',
      valor: String(m.total_usuarios),
      etiqueta: 'Usuarios registrados (reales)',
    },
    {
      id: 'lugares',
      icono: 'bi-pin-map-fill',
      colorIcono: '#c1443c',
      fondoIcono: '#fbe7e6',
      valor: String(m.total_lugares_activos),
      etiqueta: 'Lugares activos en el catálogo',
      tendencia: m.total_lugares_inactivos > 0 ? `${m.total_lugares_inactivos} dado(s) de baja` : null,
    },
    {
      id: 'itinerarios',
      icono: 'bi-calendar3',
      colorIcono: '#2e7d32',
      fondoIcono: '#e6f4ea',
      valor: String(m.total_itinerarios),
      etiqueta: 'Itinerarios creados (reales)',
    },
    {
      id: 'valoracion',
      icono: 'bi-star-fill',
      colorIcono: '#d9822b',
      fondoIcono: '#fdf0e2',
      valor: m.valoracion_promedio_general != null ? m.valoracion_promedio_general.toFixed(1) : '—',
      etiqueta: 'Valoración promedio del catálogo',
    },
    {
      id: 'arco',
      icono: 'bi-shield-exclamation',
      colorIcono: m.solicitudes_arco_pendientes > 0 ? '#c1443c' : '#6f6b64',
      fondoIcono: m.solicitudes_arco_pendientes > 0 ? '#fbe7e6' : '#eee',
      valor: String(m.solicitudes_arco_pendientes),
      etiqueta: 'Solicitudes ARCO pendientes',
    },
  ]
}

function AdminPanel() {
  const { usuario, token } = useAuth()
  const [datos, setDatos] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!token) return
    setCargando(true)
    setError('')
    obtenerPanelAdmin(token)
      .then(setDatos)
      .catch((err) => setError(err instanceof ApiError ? err.message : 'No se pudo cargar el panel.'))
      .finally(() => setCargando(false))
  }, [token])

  if (cargando) {
    return (
      <div className="container py-5 text-center text-muted">
        <span className="spinner-border spinner-border-sm me-2"></span>
        Calculando métricas en vivo...
      </div>
    )
  }

  if (error || !datos) {
    return (
      <div className="container py-5 text-center">
        <div className="alert alert-danger d-inline-block">
          <i className="bi bi-exclamation-circle me-1"></i> {error || 'No se pudo cargar el panel.'}
        </div>
      </div>
    )
  }

  const tarjetas = construirTarjetas(datos)

  return (
    <div className="container py-5">
      <div className="d-flex justify-content-between align-items-start flex-wrap gap-3 mb-4">
        <div>
          <p className="ts-eyebrow mb-1">Panel de administración</p>
          <h1 className="ts-heading mb-1">Hola, {usuario.nombre.split(' ')[0]}</h1>
          <p className="text-muted mb-0">Estado general de la plataforma, calculado en vivo.</p>
        </div>
        <span className="ts-status-badge">
          <span className="ts-status-dot"></span> Datos reales — Tiempo real
        </span>
      </div>

      {/* ---- Estadísticas ---- */}
      <div className="row row-cols-2 row-cols-lg-5 g-4 mb-4">
        {tarjetas.map((estadistica) => (
          <div className="col" key={estadistica.id}>
            <StatCard estadistica={estadistica} />
          </div>
        ))}
      </div>

      {datos.solicitudes_arco_pendientes > 0 && (
        <div className="alert alert-warning d-flex align-items-start gap-2 mb-4">
          <i className="bi bi-info-circle-fill mt-1"></i>
          <div>
            Hay {datos.solicitudes_arco_pendientes} solicitud(es) de derechos ARCO sin atender. Revisa el correo
            de contacto de la plataforma para responderlas dentro del plazo legal.
          </div>
        </div>
      )}

      {/* ---- Crecimiento + catálogo por categoría ---- */}
      <div className="row g-4 mb-4">
        <div className="col-12 col-lg-7">
          <div className="ts-chart-card">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h2 className="h6 mb-0">Crecimiento de la plataforma</h2>
              <span className="small text-muted">Últimas 6 semanas</span>
            </div>
            <LineChartTendencia
              etiquetas={datos.tendencia_semanal.etiquetas}
              serie1={datos.tendencia_semanal.usuarios_nuevos}
              etiquetaSerie1="Usuarios nuevos"
              serie2={datos.tendencia_semanal.itinerarios_nuevos}
              etiquetaSerie2="Itinerarios nuevos"
            />
          </div>
        </div>
        <div className="col-12 col-lg-5">
          <div className="ts-chart-card">
            <h2 className="h6 mb-0">Catálogo por categoría</h2>
            <p className="small text-muted mb-3">Lugares activos</p>
            {datos.lugares_por_categoria.length > 0 ? (
              <BarChartCategorias datos={datos.lugares_por_categoria} label="Lugares" />
            ) : (
              <p className="text-muted small mb-0">Todavía no hay lugares activos en el catálogo.</p>
            )}
          </div>
        </div>
      </div>

      {/* ---- Lugares mejor valorados ---- */}
      <div className="ts-chart-card">
        <h2 className="h6 mb-3">Lugares mejor valorados</h2>
        {datos.lugares_mejor_valorados.length > 0 ? (
          <ol className="list-unstyled mb-0 d-flex flex-column gap-2">
            {datos.lugares_mejor_valorados.map((lugar, indice) => (
              <li key={lugar.nombre} className="d-flex justify-content-between align-items-center">
                <span>
                  <span className="text-muted me-2">{indice + 1}.</span>
                  {lugar.nombre}
                </span>
                <span className="small text-muted">
                  <i className="bi bi-star-fill text-warning me-1"></i>
                  {lugar.valoracion_promedio.toFixed(1)} ({lugar.total_valoraciones})
                </span>
              </li>
            ))}
          </ol>
        ) : (
          <p className="text-muted small mb-0">Todavía no hay lugares con valoraciones.</p>
        )}
      </div>
    </div>
  )
}

export default AdminPanel
