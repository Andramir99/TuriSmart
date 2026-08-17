// Registro central de Chart.js. Chart.js es "modular": hay que decirle
// explícitamente qué piezas vas a usar (ejes, líneas, barras, tooltips...).
// Cualquier componente que dibuje un gráfico importa este archivo primero
// (por sus efectos secundarios, no usamos nada de lo que exporta).
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Tooltip,
  Legend,
  Filler,
)
