import { useState } from 'react'
import { Link } from 'react-router-dom'
import { claseBadgeCategoria } from '../utils/categorias.js'
import { useAuth } from '../context/AuthContext.jsx'
import { crearInteraccion } from '../services/interaccionesService.js'

// Tarjeta de destino reutilizable: la usan Home, Explorar y Mapa GIS.
// "destino" es un Lugar tal como lo devuelve el backend (GET /lugares).
function DestinoCard({ destino }) {
  const { token } = useAuth()
  const [meGusta, setMeGusta] = useState(false)
  const [enviando, setEnviando] = useState(false)

  // "Me gusta" es una señal fuerte para el perfil dinámico (Etapa 16):
  // pesa más que una simple vista. Sin sesión no se registra — no hay a
  // quién asociarle la preferencia.
  async function alternarMeGusta(evento) {
    evento.preventDefault()
    evento.stopPropagation()
    if (!token || enviando) return
    const nuevoValor = !meGusta
    setEnviando(true)
    try {
      await crearInteraccion(
        { lugar_id: destino.id, tipo_interaccion: nuevoValor ? 'me_gusta' : 'quitar_me_gusta' },
        token,
      )
      setMeGusta(nuevoValor)
    } catch {
      // si falla, el corazón simplemente no cambia de estado
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="ts-card h-100">
      <div className="ts-card-img-wrap">
        <img src={destino.imagen_url} alt={destino.nombre} className="ts-card-img" loading="lazy" />
        <span className={`ts-badge ${claseBadgeCategoria(destino.categoria.slug)}`}>
          {destino.categoria.nombre}
        </span>
        {token && (
          <button
            type="button"
            className="ts-card-like"
            onClick={alternarMeGusta}
            disabled={enviando}
            aria-pressed={meGusta}
            aria-label={meGusta ? 'Quitar me gusta' : 'Me gusta'}
            title={meGusta ? 'Quitar me gusta' : 'Me gusta'}
          >
            <i className={meGusta ? 'bi bi-heart-fill text-danger' : 'bi bi-heart'}></i>
          </button>
        )}
      </div>
      <div className="p-3">
        <h3 className="ts-card-title mb-1">{destino.nombre}</h3>
        <p className="text-muted small mb-2">
          <i className="bi bi-geo-alt"></i> {destino.distrito}
        </p>
        <div className="d-flex justify-content-between align-items-center">
          <span className="small">
            <i className="bi bi-star-fill text-warning"></i> {destino.valoracion_promedio.toFixed(1)}{' '}
            <span className="text-muted">({destino.total_valoraciones.toLocaleString('es-PE')})</span>
          </span>
          <Link to={`/explorar/${destino.id}`} className="ts-link-arrow small">
            Ver más <i className="bi bi-arrow-right"></i>
          </Link>
        </div>
      </div>
    </div>
  )
}

export default DestinoCard
