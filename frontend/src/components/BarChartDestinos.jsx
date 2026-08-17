import { Bar } from 'react-chartjs-2'
import '../utils/chartConfig.js'

function BarChartDestinos({ datos }) {
  const data = {
    labels: datos.map((destino) => destino.nombre),
    datasets: [
      {
        label: 'Recomendaciones IA',
        data: datos.map((destino) => destino.valor),
        backgroundColor: '#c1443c',
        borderRadius: 6,
        barThickness: 16,
      },
    ],
  }

  const options = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      x: { beginAtZero: true, max: 600, ticks: { stepSize: 150 }, grid: { color: '#eee' } },
      y: { grid: { display: false } },
    },
  }

  return (
    <div style={{ height: '280px' }}>
      <Bar data={data} options={options} />
    </div>
  )
}

export default BarChartDestinos
