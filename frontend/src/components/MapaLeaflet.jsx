import { useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Polyline, LayersControl, useMap } from 'react-leaflet'
import L from 'leaflet'
import { Link } from 'react-router-dom'
import { colorCategoria } from '../utils/categorias.js'
import 'leaflet/dist/leaflet.css'

const CENTRO_LIMA = [-12.08, -77.03]

// Marcador propio (un círculo de color por categoría) en vez del pin por
// defecto de Leaflet: así evitamos el problema clásico de Leaflet+Vite
// donde los íconos por defecto no cargan (rutas de imagen rotas), y de
// paso mantenemos el mismo lenguaje visual que ya usamos en toda la app.
function crearIconoCategoria(colorHex, activo) {
  const tamano = activo ? 26 : 18
  return L.divIcon({
    className: 'ts-leaflet-marker',
    html: `<span style="display:block;width:${tamano}px;height:${tamano}px;border-radius:50%;background:${colorHex};border:3px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,.4);"></span>`,
    iconSize: [tamano, tamano],
    iconAnchor: [tamano / 2, tamano / 2],
    popupAnchor: [0, -tamano / 2],
  })
}

// react-leaflet no deja mover el mapa por props directamente: hay que
// leer la instancia del mapa con useMap() desde un componente que viva
// DENTRO de <MapContainer>. Este solo existe para eso.
function ControladorDeVista({ centrarEn }) {
  const mapa = useMap()
  useEffect(() => {
    if (centrarEn) {
      mapa.flyTo(centrarEn, 15, { duration: 0.6 })
    }
  }, [centrarEn, mapa])
  return null
}

function MapaLeaflet({ lugares, seleccionadoId, onSeleccionar, centrarEn, recorridosPorDia = [] }) {
  return (
    <MapContainer center={CENTRO_LIMA} zoom={12} style={{ height: '100%', width: '100%' }} scrollWheelZoom>
      <LayersControl position="topright">
        <LayersControl.BaseLayer checked name="Calles">
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
        </LayersControl.BaseLayer>
        <LayersControl.BaseLayer name="Claro">
          <TileLayer
            attribution='&copy; OpenStreetMap &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
          />
        </LayersControl.BaseLayer>
        <LayersControl.BaseLayer name="Oscuro">
          <TileLayer
            attribution='&copy; OpenStreetMap &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />
        </LayersControl.BaseLayer>
      </LayersControl>

      <ControladorDeVista centrarEn={centrarEn} />

      {lugares.map((lugar) => (
        <Marker
          key={lugar.id}
          position={[lugar.lat, lugar.lon]}
          icon={crearIconoCategoria(colorCategoria(lugar.categoria.slug), lugar.id === seleccionadoId)}
          eventHandlers={{ click: () => onSeleccionar(lugar.id) }}
        >
          <Popup>
            <strong>{lugar.nombre}</strong>
            <br />
            {lugar.categoria.nombre} · {lugar.distrito}
            <br />
            <i className="bi bi-star-fill text-warning"></i> {lugar.valoracion_promedio.toFixed(1)}{' '}
            ({lugar.total_valoraciones})
            <br />
            <Link to={`/explorar/${lugar.id}`}>Ver más</Link>
          </Popup>
        </Marker>
      ))}

      {/* Recorrido de un itinerario: línea RECTA entre paradas del mismo
          día, no una ruta real por calles (eso requeriría un servicio de
          enrutamiento aparte, fuera del alcance de esta etapa). */}
      {recorridosPorDia.map((dia) => (
        <Polyline
          key={dia.numero}
          positions={dia.puntos}
          pathOptions={{ color: dia.color, weight: 3, dashArray: '6 8' }}
        />
      ))}
    </MapContainer>
  )
}

export default MapaLeaflet
