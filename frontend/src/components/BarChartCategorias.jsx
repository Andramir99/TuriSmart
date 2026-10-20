import { Bar } from 'react-chartjs-2'
import '../utils/chartConfig.js'

// Como BarChartDestinos (Dashboard de agencias), pero sin su escala fija
// (0-600, calibrada para conteos de interacciones): acá se cuentan
// lugares del catálogo, un volumen mucho más chico.
function BarChartCategorias({ datos, label }) {
  const data = {
    labels: datos.map((item) => item.categoria),
    datasets: [
      {
        label,
        data: datos.map((item) => item.cantidad),
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
      x: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: '#eee' } },
      y: { grid: { display: false } },
    },
  }

  return (
    <div style={{ height: '280px' }}>
      <Bar data={data} options={options} />
    </div>
  )
}

export default BarChartCategorias
