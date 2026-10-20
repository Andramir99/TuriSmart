import { Line } from 'react-chartjs-2'
import '../utils/chartConfig.js'

// Como LineChartConsultas (Dashboard de agencias), pero genérico: sin
// escala fija (esta mide crecimiento real de la plataforma, no
// consultas, y los volúmenes no son comparables entre sí).
function LineChartTendencia({ etiquetas, serie1, etiquetaSerie1, serie2, etiquetaSerie2 }) {
  const data = {
    labels: etiquetas,
    datasets: [
      {
        label: etiquetaSerie1,
        data: serie1,
        borderColor: '#c1443c',
        backgroundColor: 'rgba(193, 68, 60, 0.12)',
        tension: 0.35,
        pointRadius: 4,
        pointBackgroundColor: '#c1443c',
        fill: true,
      },
      {
        label: etiquetaSerie2,
        data: serie2,
        borderColor: '#d9822b',
        backgroundColor: 'rgba(217, 130, 43, 0.12)',
        tension: 0.35,
        pointRadius: 4,
        pointBackgroundColor: '#d9822b',
        fill: true,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom', labels: { usePointStyle: true, boxWidth: 8 } },
    },
    scales: {
      y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: '#eee' } },
      x: { grid: { display: false } },
    },
  }

  return (
    <div style={{ height: '280px' }}>
      <Line data={data} options={options} />
    </div>
  )
}

export default LineChartTendencia
