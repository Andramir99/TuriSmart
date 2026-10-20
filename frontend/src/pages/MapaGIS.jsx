import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import DestinoListItem from '../components/DestinoListItem.jsx'
import CategoryPills from '../components/CategoryPills.jsx'
import MapaLeaflet from '../components/MapaLeaflet.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import { useLugares } from '../hooks/useLugares.js'
import { obtenerLugares } from '../services/lugaresService.js'
import { obtenerMisItinerarios, obtenerItinerarioPorId } from '../services/itinerariosService.js'
import { CATEGORIAS } from '../utils/categorias.js'
import { agruparParadasPorDia } from '../utils/itinerarios.js'
import { ApiError } from '../services/api.js'
import '../styles/mapa.css'

const COLORES_DIA = ['#c1443c', '#3355cc', '#2e7d32', '#d9822b', '#7b3fb8', '#0891b2']

function MapaGIS() {
  const { autenticado, token } = useAuth()
  const [searchParams] = useSearchParams()
  const [categoriaActiva, setCategoriaActiva] = useState('todos')
  const [busqueda, setBusqueda] = useState('')
  const [seleccionadoId, setSeleccionadoId] = useState(null)
  const [centrarEn, setCentrarEn] = useState(null)

  const { lugares, cargando, error, recargar } = useLugares()

  // Si se llega desde el botón "Ver en el mapa" de un destino (ej.
  // /mapa?lugar=12), lo selecciona y centra apenas carga el catálogo.
  useEffect(() => {
    const idParam = searchParams.get('lugar')
    if (!idParam || lugares.length === 0) return
    const destino = lugares.find((item) => item.id === Number(idParam))
    if (destino) {
      setSeleccionadoId(destino.id)
      setCentrarEn([destino.lat, destino.lon])
    }
    // Solo al cargar el catálogo la primera vez; no queremos "saltar" de
    // vuelta a este lugar si el usuario ya seleccionó otro manualmente.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lugares.length])

  // ---- Modo "Cerca de mí": geolocalización + PostGIS ST_DWithin real ----
  const [cercaDeMiActivo, setCercaDeMiActivo] = useState(false)
  const [cercaDeMiLugares, setCercaDeMiLugares] = useState([])
  const [cercaDeMiCargando, setCercaDeMiCargando] = useState(false)
  const [cercaDeMiError, setCercaDeMiError] = useState('')

  function activarCercaDeMi() {
    if (!navigator.geolocation) {
      setCercaDeMiError('Tu navegador no admite geolocalización.')
      return
    }
    setCercaDeMiCargando(true)
    setCercaDeMiError('')
    navigator.geolocation.getCurrentPosition(
      (posicion) => {
        const { latitude, longitude } = posicion.coords
        obtenerLugares({ lat: latitude, lon: longitude, radioKm: 5 })
          .then((resultado) => {
            setCercaDeMiLugares(resultado)
            setCercaDeMiActivo(true)
            setCentrarEn([latitude, longitude])
          })
          .catch((err) => {
            setCercaDeMiError(
              err instanceof ApiError ? err.message : 'No se pudo buscar cerca de ti.',
            )
          })
          .finally(() => setCercaDeMiCargando(false))
      },
      () => {
        setCercaDeMiError('No pudimos acceder a tu ubicación. Revisa los permisos del navegador.')
        setCercaDeMiCargando(false)
      },
    )
  }

  function desactivarCercaDeMi() {
    setCercaDeMiActivo(false)
    setCercaDeMiLugares([])
    setCercaDeMiError('')
  }

  // ---- Modo "Ver un itinerario en el mapa" ----
  const [misItinerarios, setMisItinerarios] = useState([])
  const [itinerarioSeleccionadoId, setItinerarioSeleccionadoId] = useState('')
  const [itinerarioDetalle, setItinerarioDetalle] = useState(null)
  const [itinerarioCargando, setItinerarioCargando] = useState(false)

  useEffect(() => {
    if (!autenticado) return
    obtenerMisItinerarios(token)
      .then(setMisItinerarios)
      .catch(() => {
        // Silencioso a propósito: si esto falla, el selector simplemente
        // queda vacío — el resto del mapa sigue funcionando igual.
      })
  }, [autenticado, token])

  function seleccionarItinerario(id) {
    setItinerarioSeleccionadoId(id)
    if (!id) {
      setItinerarioDetalle(null)
      return
    }
    desactivarCercaDeMi()
    setItinerarioCargando(true)
    obtenerItinerarioPorId(id, token)
      .then((detalle) => {
        setItinerarioDetalle(detalle)
        if (detalle.detalles.length > 0) {
          const primero = detalle.detalles[0].lugar
          setCentrarEn([primero.lat, primero.lon])
        }
      })
      .catch(() => setItinerarioDetalle(null))
      .finally(() => setItinerarioCargando(false))
  }

  const modoItinerario = Boolean(itinerarioDetalle)

  const destinosFiltrados = useMemo(() => {
    if (modoItinerario) {
      // Se anota cada lugar con su progreso real (visitado / es el
      // siguiente pendiente), para que el mapa refleje en qué parte del
      // itinerario está el turista, en vez de mostrar siempre todo el
      // recorrido como si recién estuviera empezando (observación de Wu
      // en la reunión de la semana 5).
      const paradasOrdenadas = [...itinerarioDetalle.detalles].sort(
        (a, b) => a.dia_numero - b.dia_numero || a.orden - b.orden,
      )
      const siguientePendiente = paradasOrdenadas.find((parada) => !parada.visitado)
      return itinerarioDetalle.detalles.map((parada) => ({
        ...parada.lugar,
        _visitado: parada.visitado,
        _esSiguiente: siguientePendiente?.id === parada.id,
      }))
    }
    if (cercaDeMiActivo) {
      return cercaDeMiLugares
    }
    const texto = busqueda.trim().toLowerCase()
    return lugares.filter((destino) => {
      const coincideCategoria = categoriaActiva === 'todos' || destino.categoria.slug === categoriaActiva
      const coincideTexto = !texto || destino.nombre.toLowerCase().includes(texto)
      return coincideCategoria && coincideTexto
    })
  }, [modoItinerario, itinerarioDetalle, cercaDeMiActivo, cercaDeMiLugares, lugares, categoriaActiva, busqueda])

  const recorridosPorDia = useMemo(() => {
    if (!modoItinerario) return []
    return agruparParadasPorDia(itinerarioDetalle.detalles).map((dia, indice) => ({
      numero: dia.numero,
      color: COLORES_DIA[indice % COLORES_DIA.length],
      puntos: dia.paradas.map((parada) => [parada.lugar.lat, parada.lugar.lon]),
    }))
  }, [modoItinerario, itinerarioDetalle])

  function alternarSeleccion(id) {
    setSeleccionadoId((actual) => (actual === id ? null : id))
    const destino = destinosFiltrados.find((item) => item.id === id)
    if (destino) setCentrarEn([destino.lat, destino.lon])
  }

  return (
    <div className="ts-mapa-layout">
      {/* ---- Sidebar ---- */}
      <aside className="ts-mapa-sidebar">
        <div className="p-3 pb-0">
          {autenticado && misItinerarios.length > 0 && (
            <div className="mb-3">
              <label htmlFor="selectorItinerario" className="form-label small fw-semibold mb-1">
                Ver un itinerario en el mapa
              </label>
              <select
                id="selectorItinerario"
                className="form-select form-select-sm"
                value={itinerarioSeleccionadoId}
                onChange={(evento) => seleccionarItinerario(evento.target.value)}
              >
                <option value="">Catálogo completo</option>
                {misItinerarios.map((itinerario) => (
                  <option key={itinerario.id} value={itinerario.id}>
                    {itinerario.titulo}
                  </option>
                ))}
              </select>
            </div>
          )}

          {!modoItinerario && (
            <>
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
                    if (cercaDeMiActivo) desactivarCercaDeMi()
                  }}
                  disabled={cercaDeMiActivo}
                />
              </div>

              <div className="mb-3">
                <CategoryPills
                  categorias={CATEGORIAS}
                  activa={categoriaActiva}
                  onCambiar={(slug) => {
                    setCategoriaActiva(slug)
                    setSeleccionadoId(null)
                    if (cercaDeMiActivo) desactivarCercaDeMi()
                  }}
                />
              </div>

              {cercaDeMiActivo ? (
                <button type="button" className="btn btn-sm btn-outline-secondary w-100 mb-2" onClick={desactivarCercaDeMi}>
                  <i className="bi bi-x-lg me-1"></i> Quitar filtro "Cerca de mí"
                </button>
              ) : (
                <button
                  type="button"
                  className="btn btn-sm btn-light border w-100 mb-2"
                  onClick={activarCercaDeMi}
                  disabled={cercaDeMiCargando}
                >
                  {cercaDeMiCargando ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2"></span>
                      Ubicándote...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-crosshair me-1"></i> Cerca de mí (5 km)
                    </>
                  )}
                </button>
              )}
              {cercaDeMiError && <p className="text-danger small mb-2">{cercaDeMiError}</p>}
            </>
          )}

          {modoItinerario && (
            <button
              type="button"
              className="btn btn-sm btn-outline-secondary w-100 mb-2"
              onClick={() => seleccionarItinerario('')}
            >
              <i className="bi bi-x-lg me-1"></i> Volver al catálogo completo
            </button>
          )}

          <p className="text-muted small mb-1">
            {destinosFiltrados.length} destino{destinosFiltrados.length === 1 ? '' : 's'}{' '}
            {cercaDeMiActivo ? 'a menos de 5 km' : modoItinerario ? 'en este itinerario' : 'encontrados'}
          </p>
        </div>

        <div className="ts-mapa-lista px-3">
          {cargando || itinerarioCargando ? (
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

      {/* ---- Mapa real (Leaflet + OpenStreetMap) ---- */}
      <div className="ts-map-canvas">
        <span className="ts-map-badge-topleft">
          <i className="bi bi-stars"></i> {destinosFiltrados.length} destinos visibles
        </span>

        <MapaLeaflet
          lugares={destinosFiltrados}
          seleccionadoId={seleccionadoId}
          onSeleccionar={alternarSeleccion}
          centrarEn={centrarEn}
          recorridosPorDia={recorridosPorDia}
        />

        {modoItinerario && (
          <span className="ts-map-legend">
            <i className="bi bi-info-circle"></i> Las líneas conectan las paradas en línea
            recta — no es la ruta real por calles
          </span>
        )}
      </div>
    </div>
  )
}

export default MapaGIS
