function MetricaBarra({ metrica }) {
  return (
    <div className="mb-3">
      <div className="d-flex justify-content-between small mb-1">
        <span>{metrica.etiqueta}</span>
        <span className="fw-semibold">{metrica.valor}%</span>
      </div>
      <div className="ts-progress-track">
        <div
          className="ts-progress-fill"
          style={{ width: `${metrica.valor}%`, backgroundColor: metrica.color }}
        ></div>
      </div>
    </div>
  )
}

export default MetricaBarra
