import { Line } from 'react-chartjs-2'
import '../utils/chartConfig.js'

function LineChartConsultas({ datos }) {
  const data = {
    labels: datos.etiquetas,
    datasets: [
      {
        label: 'Consultas',
        data: datos.consultas,
        borderColor: '#c1443c',
        backgroundColor: 'rgba(193, 68, 60, 0.12)',
        tension: 0.35,
        pointRadius: 4,
        pointBackgroundColor: '#c1443c',
        fill: true,
      },
      {
        label: 'Itinerarios',
        data: datos.itinerarios,
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
      y: { beginAtZero: true, max: 600, ticks: { stepSize: 150 }, grid: { color: '#eee' } },
      x: { grid: { display: false } },
    },
  }

  return (
    <div style={{ height: '280px' }}>
      <Line data={data} options={options} />
    </div>
  )
}

export default LineChartConsultas
