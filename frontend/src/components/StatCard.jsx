function StatCard({ estadistica }) {
  return (
    <div className="ts-card h-100 p-4">
      <div className="d-flex justify-content-between align-items-start mb-3">
        <span
          className="ts-stat-icon"
          style={{ backgroundColor: estadistica.fondoIcono, color: estadistica.colorIcono }}
        >
          <i className={`bi ${estadistica.icono}`}></i>
        </span>
        <span className="small text-success fw-semibold">
          <i className="bi bi-graph-up-arrow me-1"></i>
          {estadistica.tendencia}
        </span>
      </div>
      <p className="h4 mb-1">{estadistica.valor}</p>
      <p className="text-muted small mb-0">{estadistica.etiqueta}</p>
    </div>
  )
}

export default StatCard
