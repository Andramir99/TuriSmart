import { useCallback, useEffect, useState } from 'react'
import { obtenerLugares } from '../services/lugaresService.js'
import { ApiError } from '../services/api.js'

// Hook compartido por Home, Explorar y Mapa GIS: las tres necesitan la
// misma lista completa de lugares y la filtran/recortan cada una a su
// manera, así que la carga desde el backend vive en un solo lugar.
export function useLugares() {
  const [lugares, setLugares] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')

  const recargar = useCallback(() => {
    setCargando(true)
    setError('')
    obtenerLugares()
      .then(setLugares)
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : 'No se pudieron cargar los destinos.')
      })
      .finally(() => setCargando(false))
  }, [])

  useEffect(() => {
    recargar()
  }, [recargar])

  return { lugares, cargando, error, recargar }
}
