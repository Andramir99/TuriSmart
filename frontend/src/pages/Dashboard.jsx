import { useEffect, useState } from 'react'
import StatCard from '../components/StatCard.jsx'
import LineChartConsultas from '../components/LineChartConsultas.jsx'
import BarChartDestinos from '../components/BarChartDestinos.jsx'
import MetricaBarra from '../components/MetricaBarra.jsx'
import HeatMapMock from '../components/HeatMapMock.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import { obtenerDashboard } from '../services/analiticaService.js'
import { formatearFechaCompleta, formatearFechaTabla } from '../utils/fechas.js'
import { ApiError } from '../services/api.js'
import '../styles/dashboard.css'

// Mapea las estadísticas reales del backend a la forma que espera
// StatCard (icono/colores son solo presentación, no vienen de la API).
function construirTarjetas(estadisticas) {
  return [
    {
      id: 'itinerarios',
      icono: 'bi-calendar3',
      colorIcono: '#c1443c',
      fondoIcono: '#fbe7e6',
      valor: String(estadisticas.total_itinerarios),
      etiqueta: 'Itinerarios creados (usuarios reales)',
    },
    {
      id: 'satisfaccion',
      icono: 'bi-star-fill',
      colorIcono: '#d9822b',
      fondoIcono: '#fdf0e2',
      valor: estadisticas.promedio_valoracion != null ? estadisticas.promedio_valoracion.toFixed(1) : '—',
      etiqueta: 'Valoración promedio',
    },
    {
      id: 'destino',
      icono: 'bi-geo-alt-fill',
      colorIcono: '#3355cc',
      fondoIcono: '#e8eefc',
      valor: estadisticas.destino_mas_valorado || 'Sin datos todavía',
      etiqueta: 'Destino más valorado',
      tendencia:
        estadisticas.destino_mas_valorado_total > 0
          ? `${estadisticas.destino_mas_valorado_total} valoraciones`
          : null,
    },
    {
      id: 'aceptacion',
      icono: 'bi-hand-thumbs-up-fill',
      colorIcono: '#2e7d32',
      fondoIcono: '#e6f4ea',
      valor:
        estadisticas.tasa_aceptacion_recomendaciones != null
          ? `${estadisticas.tasa_aceptacion_recomendaciones}%`
          : '—',
      etiqueta: 'Recomendaciones IA aceptadas',
      tendencia:
        estadisticas.total_reacciones_recomendaciones > 0
          ? `${estadisticas.total_reacciones_recomendaciones} reacciones`
          : null,
    },
  ]
}

function Dashboard() {
  const { token } = useAuth()
  const [datos, setDatos] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!token) return
    setCargando(true)
    setError('')
    obtenerDashboard(token)
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

  const tarjetas = construirTarjetas(datos.estadisticas)

  return (
    <div className="container py-5">
      <div className="d-flex justify-content-between align-items-start flex-wrap gap-3 mb-4">
        <div>
          <p className="ts-eyebrow mb-1">Panel analítico</p>
          <h1 className="ts-heading mb-1">Dashboard</h1>
          <p className="text-muted mb-0">
            TuriSmart Lima · calculado en vivo, {formatearFechaCompleta(new Date().toISOString().slice(0, 10))}
          </p>
        </div>
        <span className="ts-status-badge">
          <span className="ts-status-dot"></span> Datos reales — Tiempo real
        </span>
      </div>

      {!datos.datos_suficientes && (
        <div className="alert alert-warning d-flex align-items-start gap-2 mb-4">
          <i className="bi bi-info-circle-fill mt-1"></i>
          <div>
            <strong>Uso real todavía limitado.</strong> Estas métricas excluyen a propósito los datos
            sintéticos de prueba, así que con pocos itinerarios reales los números se ven chicos — es
            preferible mostrar la verdad a inflar el panel con datos de prueba disfrazados de reales.
          </div>
        </div>
      )}

      {/* ---- Estadísticas ---- */}
      <div className="row g-4 mb-4">
        {tarjetas.map((estadistica) => (
          <div className="col-6 col-lg-3" key={estadistica.id}>
            <StatCard estadistica={estadistica} />
          </div>
        ))}
      </div>

      {/* ---- Tendencia + mapa de calor ---- */}
      <div className="row g-4 mb-4">
        <div className="col-12 col-lg-8">
          <div className="ts-chart-card">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h2 className="h6 mb-0">Tendencia de consultas semanales</h2>
              <span className="small text-muted">Últimas 6 semanas</span>
            </div>
            <LineChartConsultas datos={datos.tendencia_semanal} />
          </div>
        </div>
        <div className="col-12 col-lg-4">
          <div className="ts-chart-card">
            <h2 className="h6 mb-0">Flujos turísticos GIS</h2>
            <p className="small text-muted mb-3">Mapa de calor ilustrativo — Lima Metropolitana</p>
            <HeatMapMock />
          </div>
        </div>
      </div>

      {/* ---- Destinos más visitados + métricas de usuario ---- */}
      <div className="row g-4 mb-4">
        <div className="col-12 col-lg-8">
          <div className="ts-chart-card">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h2 className="h6 mb-0">Destinos más vistos</h2>
              <span className="small text-muted">Por interacciones reales</span>
            </div>
            {datos.destinos_mas_vistos.length > 0 ? (
              <BarChartDestinos datos={datos.destinos_mas_vistos} />
            ) : (
              <p className="text-muted small mb-0">Todavía no hay suficientes vistas registradas.</p>
            )}
          </div>
        </div>
        <div className="col-12 col-lg-4">
          <div className="ts-chart-card">
            <h2 className="h6 mb-3">Tipo de viaje</h2>
            {datos.metricas_tipo_grupo.length > 0 ? (
              datos.metricas_tipo_grupo.map((metrica) => <MetricaBarra metrica={metrica} key={metrica.etiqueta} />)
            ) : (
              <p className="text-muted small mb-0">Todavía no hay itinerarios reales suficientes.</p>
            )}
          </div>
        </div>
      </div>

      {/* ---- Últimos itinerarios generados ---- */}
      <div className="ts-chart-card">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h2 className="h6 mb-0">Últimos itinerarios generados</h2>
          <span className="small text-muted">Usuarios reales</span>
        </div>
        {datos.itinerarios_recientes.length > 0 ? (
          <div className="table-responsive">
            <table className="table align-middle">
              <thead className="ts-tabla-header">
                <tr>
                  <th>Usuario</th>
                  <th>Destinos</th>
                  <th>Días</th>
                  <th>Satisfacción</th>
                  <th>Fecha</th>
                </tr>
              </thead>
              <tbody>
                {datos.itinerarios_recientes.map((fila) => (
                  <tr key={fila.id}>
                    <td>
                      <div className="d-flex align-items-center gap-2">
                        <span className="ts-tabla-avatar" style={{ backgroundColor: fila.color }}>
                          {fila.usuario.charAt(0)}
                        </span>
                        {fila.usuario}
                      </div>
                    </td>
                    <td className="text-muted">{fila.destinos}</td>
                    <td>
                      {fila.dias} día{fila.dias === 1 ? '' : 's'}
                    </td>
                    <td>
                      {fila.satisfaccion != null ? (
                        <>
                          <i className="bi bi-star-fill text-warning"></i> {fila.satisfaccion.toFixed(1)}
                        </>
                      ) : (
                        <span className="text-muted">Sin calificar</span>
                      )}
                    </td>
                    <td className="text-muted">{formatearFechaTabla(fila.fecha)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-muted small mb-0">Todavía no hay itinerarios de usuarios reales.</p>
        )}
      </div>
    </div>
  )
}

export default Dashboard
