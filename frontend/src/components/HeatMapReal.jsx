import { useEffect } from 'react'
import { MapContainer, TileLayer, useMap } from 'react-leaflet'
import { HeatLayer } from 'leaflet.heat'
import 'leaflet/dist/leaflet.css'

// Mapa de calor real (Objetivo Específico 4): reemplaza a HeatMapMock.jsx,
// que dibujaba posiciones e intensidades fijas. Acá los puntos vienen de
// GET /analitica/dashboard -> mapa_calor, calculados en el backend a
// partir de interacciones y valoraciones reales sobre las coordenadas
// PostGIS de cada lugar (ver analitica_service.obtener_mapa_calor).
const CENTRO_LIMA = [-12.08, -77.03]

function CapaDeCalor({ puntos }) {
  const mapa = useMap()

  useEffect(() => {
    if (!puntos.length) return undefined

    const capa = new HeatLayer(
      puntos.map((punto) => [punto.lat, punto.lon, punto.intensidad]),
      { radius: 30, blur: 24, maxZoom: 15, minOpacity: 0.3 },
    )
    capa.addTo(mapa)
    return () => {
      mapa.removeLayer(capa)
    }
  }, [puntos, mapa])

  return null
}

function HeatMapReal({ puntos }) {
  return (
    <MapContainer
      center={CENTRO_LIMA}
      zoom={11}
      style={{ height: '220px', width: '100%', borderRadius: '8px' }}
      scrollWheelZoom={false}
      dragging={false}
      doubleClickZoom={false}
      zoomControl={false}
      attributionControl={false}
    >
      {/* Mismo tile de OpenStreetMap que el Mapa GIS, con el filtro "claro"
          (ver .ts-tiles-claro en mapa.css): CartoDB exige API key y
          Wikimedia Maps bloquea el hotlinking, así que se evita depender
          de un proveedor de tiles aparte. */}
      <TileLayer
        className="ts-tiles-claro"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <CapaDeCalor puntos={puntos} />
    </MapContainer>
  )
}

export default HeatMapReal
