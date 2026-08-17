import { useState } from 'react'
import { Link } from 'react-router-dom'
import { claseBadgeCategoria } from '../utils/categorias.js'
import { useAuth } from '../context/AuthContext.jsx'
import { crearInteraccion } from '../services/interaccionesService.js'

const ETIQUETAS_DISTANCIA = {
  cerca: { texto: 'Cerca de tu punto de partida', icono: 'bi-geo-alt-fill', clase: 'text-success' },
  moderada: { texto: 'Distancia moderada', icono: 'bi-signpost-split', clase: 'text-warning' },
  lejos: { texto: 'Lejos de tu punto de partida', icono: 'bi-signpost-2-fill', clase: 'text-danger' },
}

// Tarjeta de una recomendación del recomendador inicial (Etapa 9): a
// diferencia de DestinoCard, aquí el dato central es el "motivo" — la
// explicación de por qué el sistema sugirió justo este lugar. Desde la
// Etapa 12, además deja reaccionar "¿fue útil?" — esa reacción es lo que
// cierra el ciclo: la recomendación se genera, se muestra, y ahora queda
// registrado si el usuario la aceptó o no (recomendaciones.fue_aceptada).
function RecomendacionCard({ recomendacion }) {
  const { lugar, motivo, puntuacion, distancia_km: distanciaKm, distancia_etiqueta: distanciaEtiqueta } =
    recomendacion
  const infoDistancia = distanciaEtiqueta ? ETIQUETAS_DISTANCIA[distanciaEtiqueta] : null
  const { token } = useAuth()
  const [reaccion, setReaccion] = useState(null) // null | 'aceptada' | 'rechazada'
  const [enviando, setEnviando] = useState(false)

  async function reaccionar(tipo) {
    if (enviando || reaccion) return
    setEnviando(true)
    try {
      await crearInteraccion(
        { lugar_id: lugar.id, tipo_interaccion: `recomendacion_${tipo}` },
        token,
      )
      setReaccion(tipo)
    } catch {
      // Si falla, simplemente no se marca como reaccionado — el usuario
      // puede volver a intentarlo. No bloqueamos el resto de la tarjeta
      // por esto.
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="ts-card h-100">
      <div className="ts-card-img-wrap">
        <img src={lugar.imagen_url} alt={lugar.nombre} className="ts-card-img" loading="lazy" />
        <span className={`ts-badge ${claseBadgeCategoria(lugar.categoria.slug)}`}>
          {lugar.categoria.nombre}
        </span>
      </div>
      <div className="p-3">
        <div className="d-flex justify-content-between align-items-start mb-1">
          <h3 className="ts-card-title mb-0">{lugar.nombre}</h3>
          <span className="ts-badge-inline ts-badge--natural flex-shrink-0">
            {Math.round(puntuacion * 100)}% afinidad
          </span>
        </div>
        <p className="text-muted small mb-1">
          <i className="bi bi-geo-alt"></i> {lugar.distrito}
        </p>
        {infoDistancia && (
          <p className={`small mb-2 ${infoDistancia.clase}`}>
            <i className={`bi ${infoDistancia.icono} me-1`}></i>
            {infoDistancia.texto}
            {distanciaKm != null && ` (${distanciaKm} km)`}
          </p>
        )}
        <p className="small mb-2">
          <i className="bi bi-stars text-danger me-1"></i>
          {motivo}
        </p>

        <div className="d-flex justify-content-between align-items-center">
          <Link to={`/explorar/${lugar.id}`} className="ts-link-arrow small">
            Ver más <i className="bi bi-arrow-right"></i>
          </Link>

          {reaccion ? (
            <span className="small text-muted">
              {reaccion === 'aceptada' ? (
                <>
                  <i className="bi bi-hand-thumbs-up-fill text-success"></i> Útil
                </>
              ) : (
                <>
                  <i className="bi bi-hand-thumbs-down-fill text-secondary"></i> No útil
                </>
              )}
            </span>
          ) : (
            <div className="d-flex gap-1">
              <button
                type="button"
                className="btn btn-sm btn-light border py-0 px-2"
                onClick={() => reaccionar('aceptada')}
                disabled={enviando}
                aria-label="Marcar esta recomendación como útil"
                title="¿Fue útil?"
              >
                <i className="bi bi-hand-thumbs-up"></i>
              </button>
              <button
                type="button"
                className="btn btn-sm btn-light border py-0 px-2"
                onClick={() => reaccionar('rechazada')}
                disabled={enviando}
                aria-label="Marcar esta recomendación como no útil"
                title="¿No fue útil?"
              >
                <i className="bi bi-hand-thumbs-down"></i>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default RecomendacionCard
