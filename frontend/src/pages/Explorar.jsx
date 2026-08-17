import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import DestinoCard from '../components/DestinoCard.jsx'
import CategoryPills from '../components/CategoryPills.jsx'
import destinosMock from '../data/destinosMock.js'
import { CATEGORIAS } from '../utils/categorias.js'

function Explorar() {
  // useSearchParams lee/escribe el "?q=..." de la URL. Así, si llegas aquí
  // desde el buscador de la Home (que navega a /explorar?q=museo), esta
  // página abre ya con ese texto precargado en su propio buscador.
  const [searchParams, setSearchParams] = useSearchParams()
  const [categoriaActiva, setCategoriaActiva] = useState('todos')
  const [busqueda, setBusqueda] = useState(searchParams.get('q') || '')

  useEffect(() => {
    const query = searchParams.get('q')
    if (query) setBusqueda(query)
  }, [searchParams])

  const destinosFiltrados = useMemo(() => {
    const texto = busqueda.trim().toLowerCase()
    return destinosMock.filter((destino) => {
      const coincideCategoria = categoriaActiva === 'todos' || destino.categoria === categoriaActiva
      const coincideTexto =
        !texto ||
        destino.nombre.toLowerCase().includes(texto) ||
        destino.distrito.toLowerCase().includes(texto)
      return coincideCategoria && coincideTexto
    })
  }, [categoriaActiva, busqueda])

  function manejarSubmit(evento) {
    evento.preventDefault()
    setSearchParams(busqueda ? { q: busqueda } : {})
  }

  return (
    <div className="container py-5">
      <p className="ts-eyebrow mb-1">Destinos destacados</p>
      <h1 className="ts-heading mb-4">Lima te espera</h1>

      <form className="mb-4" style={{ maxWidth: '420px' }} onSubmit={manejarSubmit}>
        <div className="input-group">
          <span className="input-group-text bg-white border-end-0">
            <i className="bi bi-search text-muted"></i>
          </span>
          <input
            type="search"
            className="form-control border-start-0"
            placeholder="Buscar destinos..."
            value={busqueda}
            onChange={(evento) => setBusqueda(evento.target.value)}
            aria-label="Buscar destinos"
          />
        </div>
      </form>

      <div className="mb-4">
        <CategoryPills
          categorias={CATEGORIAS}
          activa={categoriaActiva}
          onCambiar={setCategoriaActiva}
        />
      </div>

      <p className="text-muted small mb-3">
        {destinosFiltrados.length} destino{destinosFiltrados.length === 1 ? '' : 's'} encontrado
        {destinosFiltrados.length === 1 ? '' : 's'}
      </p>

      {destinosFiltrados.length === 0 ? (
        <div className="alert alert-light border">
          No encontramos destinos con ese filtro. Prueba con otra búsqueda o categoría.
        </div>
      ) : (
        <div className="row g-4">
          {destinosFiltrados.map((destino) => (
            <div className="col-6 col-lg-3" key={destino.id}>
              <DestinoCard destino={destino} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Explorar
