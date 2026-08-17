import dashboardMock from '../data/dashboardMock.js'
import StatCard from '../components/StatCard.jsx'
import LineChartConsultas from '../components/LineChartConsultas.jsx'
import BarChartDestinos from '../components/BarChartDestinos.jsx'
import MetricaBarra from '../components/MetricaBarra.jsx'
import HeatMapMock from '../components/HeatMapMock.jsx'
import { formatearFechaCompleta, formatearFechaTabla } from '../utils/fechas.js'
import '../styles/dashboard.css'

function Dashboard() {
  return (
    <div className="container py-5">
      <div className="d-flex justify-content-between align-items-start flex-wrap gap-3 mb-4">
        <div>
          <p className="ts-eyebrow mb-1">Panel analítico</p>
          <h1 className="ts-heading mb-1">Dashboard</h1>
          <p className="text-muted mb-0">
            Agencia TuriSmart Lima · {formatearFechaCompleta(dashboardMock.actualizadoEn)}
          </p>
        </div>
        <span className="ts-status-badge">
          <span className="ts-status-dot"></span> Sistema operativo — Tiempo real
        </span>
      </div>

      {/* ---- Estadísticas ---- */}
      <div className="row g-4 mb-4">
        {dashboardMock.estadisticas.map((estadistica) => (
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
            <LineChartConsultas datos={dashboardMock.tendenciaSemanal} />
          </div>
        </div>
        <div className="col-12 col-lg-4">
          <div className="ts-chart-card">
            <h2 className="h6 mb-0">Flujos turísticos GIS</h2>
            <p className="small text-muted mb-3">Mapa de calor — Lima Metropolitana</p>
            <HeatMapMock />
          </div>
        </div>
      </div>

      {/* ---- Destinos más visitados + métricas de usuario ---- */}
      <div className="row g-4 mb-4">
        <div className="col-12 col-lg-8">
          <div className="ts-chart-card">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h2 className="h6 mb-0">Destinos más visitados</h2>
              <span className="small text-muted">Por recomendaciones IA</span>
            </div>
            <BarChartDestinos datos={dashboardMock.destinosMasVisitados} />
          </div>
        </div>
        <div className="col-12 col-lg-4">
          <div className="ts-chart-card">
            <h2 className="h6 mb-3">Métricas de usuario</h2>
            {dashboardMock.metricasUsuario.map((metrica) => (
              <MetricaBarra metrica={metrica} key={metrica.etiqueta} />
            ))}
          </div>
        </div>
      </div>

      {/* ---- Últimos itinerarios generados ---- */}
      <div className="ts-chart-card">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h2 className="h6 mb-0">Últimos itinerarios generados</h2>
          <span className="small text-muted">Esta semana</span>
        </div>
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
              {dashboardMock.itinerariosRecientes.map((fila) => (
                <tr key={fila.id}>
                  <td>
                    <div className="d-flex align-items-center gap-2">
                      <span
                        className="ts-tabla-avatar"
                        style={{ backgroundColor: fila.color }}
                      >
                        {fila.usuario.charAt(0)}
                      </span>
                      {fila.usuario}
                    </div>
                  </td>
                  <td className="text-muted">{fila.destinos}</td>
                  <td>{fila.dias} día{fila.dias === 1 ? '' : 's'}</td>
                  <td>
                    <i className="bi bi-star-fill text-warning"></i> {fila.satisfaccion.toFixed(1)}
                  </td>
                  <td className="text-muted">{formatearFechaTabla(fila.fecha)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
