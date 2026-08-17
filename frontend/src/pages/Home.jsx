import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import DestinoCard from '../components/DestinoCard.jsx'
import CategoryPills from '../components/CategoryPills.jsx'
import { useLugares } from '../hooks/useLugares.js'
import { CATEGORIAS } from '../utils/categorias.js'
import '../styles/home.css'

const HERO_IMAGE = 'https://picsum.photos/seed/lima-malecon-hero/1600/900'
const MAX_DESTACADOS = 8

function Home() {
  const navigate = useNavigate()
  const [categoriaActiva, setCategoriaActiva] = useState('todos')
  const [busqueda, setBusqueda] = useState('')
  const { lugares, cargando, error, recargar } = useLugares()

  const destinosFiltrados = useMemo(() => {
    const filtrados =
      categoriaActiva === 'todos'
        ? lugares
        : lugares.filter((destino) => destino.categoria.slug === categoriaActiva)
    return filtrados.slice(0, MAX_DESTACADOS)
  }, [lugares, categoriaActiva])

  function manejarBusqueda(evento) {
    evento.preventDefault()
    const query = busqueda.trim()
    navigate(query ? `/explorar?q=${encodeURIComponent(query)}` : '/explorar')
  }

  return (
    <div>
      {/* ---- Hero ---- */}
      <section className="ts-hero" style={{ backgroundImage: `url(${HERO_IMAGE})` }}>
        <span className="ts-hero-badge">
          <i className="bi bi-stars"></i> IA activa
        </span>

        <div className="container ts-hero-inner">
          <p className="ts-eyebrow mb-3">Lima, Perú — Turismo inteligente</p>
          <h1 className="ts-hero-title mb-3">
            Descubre Lima
            <br />
            como nunca antes
          </h1>
          <p className="mx-auto mb-4" style={{ maxWidth: '560px', opacity: 0.9 }}>
            Itinerarios inteligentes personalizados con IA y mapas en tiempo real para tu
            visita perfecta a Lima.
          </p>

          <div className="d-flex justify-content-center gap-3 flex-wrap mb-4">
            <Link to="/planificar" className="btn btn-ts-primary rounded-pill px-4 py-2">
              <i className="bi bi-stars me-1"></i> Planifica tu viaje
            </Link>
            <Link to="/explorar" className="btn btn-outline-light rounded-pill px-4 py-2">
              <i className="bi bi-map me-1"></i> Ver destinos
            </Link>
          </div>

          <form className="d-flex ts-hero-search" onSubmit={manejarBusqueda}>
            <input
              type="search"
              className="form-control"
              placeholder="Busca museos, playas, restaurantes en Lima..."
              value={busqueda}
              onChange={(evento) => setBusqueda(evento.target.value)}
              aria-label="Buscar destinos"
            />
            <button type="submit" className="btn btn-ts-primary">
              Buscar
            </button>
          </form>
        </div>
      </section>

      {/* ---- Estadísticas ---- */}
      <section className="ts-stats-bar py-4 border-bottom">
        <div className="container">
          <div className="row text-center g-4">
            <div className="col-6 col-md-3">
              <div className="ts-stat-number">127+</div>
              <div className="small text-muted">Destinos en Lima</div>
            </div>
            <div className="col-6 col-md-3">
              <div className="ts-stat-number">4.8★</div>
              <div className="small text-muted">Satisfacción media</div>
            </div>
            <div className="col-6 col-md-3">
              <div className="ts-stat-number">12K+</div>
              <div className="small text-muted">Viajeros activos</div>
            </div>
            <div className="col-6 col-md-3">
              <div className="ts-stat-number">98%</div>
              <div className="small text-muted">Recomendarían</div>
            </div>
          </div>
        </div>
      </section>

      {/* ---- Destinos destacados ---- */}
      <section className="py-5">
        <div className="container">
          <div className="d-flex justify-content-between align-items-end flex-wrap gap-2 mb-4">
            <div>
              <p className="ts-eyebrow mb-1">Destinos destacados</p>
              <h2 className="ts-heading mb-0">Lima te espera</h2>
            </div>
            <Link to="/mapa" className="ts-link-arrow">
              Ver todos en el mapa <i className="bi bi-arrow-right"></i>
            </Link>
          </div>

          <div className="mb-4">
            <CategoryPills
              categorias={CATEGORIAS}
              activa={categoriaActiva}
              onCambiar={setCategoriaActiva}
            />
          </div>

          {cargando ? (
            <div className="text-center text-muted py-5">
              <span className="spinner-border spinner-border-sm me-2"></span>
              Cargando destinos...
            </div>
          ) : error ? (
            <div className="alert alert-danger d-flex justify-content-between align-items-center">
              <span>
                <i className="bi bi-exclamation-circle me-1"></i> {error}
              </span>
              <button type="button" className="btn btn-sm btn-outline-danger" onClick={recargar}>
                Reintentar
              </button>
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
      </section>

      {/* ---- Por qué TuriSmart ---- */}
      <section className="ts-section-dark py-5">
        <div className="container text-center">
          <p className="ts-eyebrow mb-1">Tecnología turística</p>
          <h2 className="ts-heading text-white mb-5">Por qué TuriSmart</h2>

          <div className="row g-4 text-start">
            <div className="col-md-4">
              <div className="ts-feature-card">
                <div className="ts-feature-icon ts-feature-icon--orange">
                  <i className="bi bi-stars"></i>
                </div>
                <h3 className="h5 text-white mb-2">IA Personalizada</h3>
                <p className="small mb-0">
                  Algoritmos de Machine Learning que aprenden tus preferencias y generan
                  rutas únicas adaptadas a tu estilo de viaje.
                </p>
              </div>
            </div>
            <div className="col-md-4">
              <div className="ts-feature-card">
                <div className="ts-feature-icon ts-feature-icon--blue">
                  <i className="bi bi-map"></i>
                </div>
                <h3 className="h5 text-white mb-2">Mapas GIS en tiempo real</h3>
                <p className="small mb-0">
                  Datos geoespaciales actualizados: tráfico, clima, afluencia y capas
                  temáticas sobre Lima Metropolitana.
                </p>
              </div>
            </div>
            <div className="col-md-4">
              <div className="ts-feature-card">
                <div className="ts-feature-icon ts-feature-icon--green">
                  <i className="bi bi-clipboard-check"></i>
                </div>
                <h3 className="h5 text-white mb-2">Itinerarios inteligentes</h3>
                <p className="small mb-0">
                  Planifica, edita y comparte tu itinerario. CRUD completo con estimación
                  de presupuesto y distancias.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ---- CTA final ---- */}
      <section className="ts-section-cta py-5 text-center">
        <div className="container">
          <span className="ts-cta-badge mb-3">
            <i className="bi bi-geo-alt text-danger"></i> Recomendado por guías locales
          </span>
          <h2 className="ts-heading mb-3">¿Listo para descubrir Lima?</h2>
          <p className="text-muted mb-4">
            Genera tu itinerario personalizado en menos de 2 minutos. Gratis, sin registro
            previo.
          </p>
          <Link to="/planificar" className="btn btn-ts-primary rounded-pill px-4 py-2">
            <i className="bi bi-stars me-1"></i> Generar mi itinerario con IA
          </Link>
        </div>
      </section>
    </div>
  )
}

export default Home
