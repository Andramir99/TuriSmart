import { useMemo, useState } from 'react'
import DestinoListItem from '../components/DestinoListItem.jsx'
import CategoryPills from '../components/CategoryPills.jsx'
import { useLugares } from '../hooks/useLugares.js'
import { CATEGORIAS, colorCategoria } from '../utils/categorias.js'
import { proyectarPosicion, ETIQUETAS_DISTRITOS_MOCK } from '../utils/mapaMock.js'
import '../styles/mapa.css'

// Capas del panel superior derecho. Por ahora son solo visuales (no
// prenden ni apagan nada real): la capa de tráfico/clima/afluencia de
// verdad se conecta en la Etapa 11 junto con Leaflet.
const CAPAS_MOCK = [
  { id: 'trafico', etiqueta: 'Tráfico', icono: 'bi-signpost-split' },
  { id: 'clima', etiqueta: 'Clima', icono: 'bi-cloud-sun' },
  { id: 'afluencia', etiqueta: 'Afluencia', icono: 'bi-people' },
]

function MapaGIS() {
  const [categoriaActiva, setCategoriaActiva] = useState('todos')
  const [busqueda, setBusqueda] = useState('')
  const [seleccionadoId, setSeleccionadoId] = useState(null)
  const { lugares, cargando, error, recargar } = useLugares()

  const destinosFiltrados = useMemo(() => {
    const texto = busqueda.trim().toLowerCase()
    return lugares.filter((destino) => {
      const coincideCategoria = categoriaActiva === 'todos' || destino.categoria.slug === categoriaActiva
      const coincideTexto = !texto || destino.nombre.toLowerCase().includes(texto)
      return coincideCategoria && coincideTexto
    })
  }, [lugares, categoriaActiva, busqueda])

  function cambiarCategoria(slug) {
    setCategoriaActiva(slug)
    setSeleccionadoId(null)
  }

  function alternarSeleccion(id) {
    setSeleccionadoId((actual) => (actual === id ? null : id))
  }

  return (
    <div className="ts-mapa-layout">
      {/* ---- Sidebar ---- */}
      <aside className="ts-mapa-sidebar">
        <div className="p-3 pb-0">
          <div className="input-group mb-3">
            <span className="input-group-text bg-white border-end-0">
              <i className="bi bi-search text-muted"></i>
            </span>
            <input
              type="search"
              className="form-control border-start-0"
              placeholder="Buscar destinos..."
              value={busqueda}
              onChange={(evento) => {
                setBusqueda(evento.target.value)
                setSeleccionadoId(null)
              }}
            />
          </div>

          <div className="mb-3">
            <CategoryPills
              categorias={CATEGORIAS}
              activa={categoriaActiva}
              onCambiar={cambiarCategoria}
            />
          </div>

          <p className="text-muted small mb-1">
            {destinosFiltrados.length} destinos encontrados
          </p>
        </div>

        <div className="ts-mapa-lista px-3">
          {cargando ? (
            <p className="text-muted small py-4 text-center">
              <span className="spinner-border spinner-border-sm me-2"></span>
              Cargando destinos...
            </p>
          ) : error ? (
            <div className="text-center py-4">
              <p className="text-danger small mb-2">
                <i className="bi bi-exclamation-circle me-1"></i> {error}
              </p>
              <button type="button" className="btn btn-sm btn-outline-danger" onClick={recargar}>
                Reintentar
              </button>
            </div>
          ) : (
            <>
              {destinosFiltrados.map((destino) => (
                <DestinoListItem
                  key={destino.id}
                  destino={destino}
                  activo={destino.id === seleccionadoId}
                  onSeleccionar={alternarSeleccion}
                />
              ))}
              {destinosFiltrados.length === 0 && (
                <p className="text-muted small py-4 text-center">
                  Sin resultados para este filtro.
                </p>
              )}
            </>
          )}
        </div>
      </aside>

      {/* ---- Lienzo del mapa (maqueta visual) ---- */}
      <div className="ts-map-canvas">
        <span className="ts-map-badge-topleft">
          <i className="bi bi-stars"></i> IA activa — {destinosFiltrados.length} destinos
          visibles
        </span>

        <div className="ts-map-layers-panel">
          <h6 className="mb-2">Capas</h6>
          {CAPAS_MOCK.map((capa) => (
            <div className="ts-map-layer-row" key={capa.id}>
              <span>
                <i className={`bi ${capa.icono} me-1`}></i>
                {capa.etiqueta}
              </span>
              <span className="ts-dot"></span>
            </div>
          ))}
        </div>

        {ETIQUETAS_DISTRITOS_MOCK.map((etiqueta) => (
          <span
            key={etiqueta.nombre}
            className="ts-map-district-label"
            style={{ top: etiqueta.top, left: etiqueta.left }}
          >
            {etiqueta.nombre}
          </span>
        ))}

        {destinosFiltrados.map((destino) => {
          const posicion = proyectarPosicion(destino.lat, destino.lon)
          const activo = destino.id === seleccionadoId
          return (
            <div
              key={destino.id}
              className={`ts-marker${activo ? ' ts-marker--active' : ''}`}
              style={{ top: posicion.top, left: posicion.left }}
              onClick={() => alternarSeleccion(destino.id)}
              title={destino.nombre}
            >
              {activo && (
                <div className="ts-marker-popup">
                  <p className="fw-semibold mb-1">{destino.nombre}</p>
                  <p className="mb-0 text-muted">
                    <i className="bi bi-star-fill text-warning"></i>{' '}
                    {destino.valoracion_promedio.toFixed(1)} · {destino.categoria.nombre}
                  </p>
                </div>
              )}
              <span
                className="ts-marker-dot"
                style={{ backgroundColor: colorCategoria(destino.categoria.slug) }}
              ></span>
            </div>
          )
        })}

        <span className="ts-map-legend">
          <i className="bi bi-info-circle"></i> Maqueta visual — el mapa real con Leaflet llega
          en la Etapa 11
        </span>
      </div>
    </div>
  )
}

export default MapaGIS
