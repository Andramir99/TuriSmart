import { NavLink, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

// NavLink (a diferencia de Link) sabe si su URL coincide con la página actual
// y nos pasa "isActive" para pintar el link seleccionado en rojo, igual que
// en el Figma (por ejemplo "Dashboard" resaltado cuando estás en /dashboard).
function navLinkClass({ isActive }) {
  return (
    'nav-link-ts d-flex align-items-center gap-2 px-3 py-2 rounded-pill' +
    (isActive ? ' nav-link-ts--active' : '')
  )
}

function Navbar() {
  const { usuario, autenticado, cerrarSesion } = useAuth()
  const navigate = useNavigate()
  const esAdmin = usuario?.rol === 'admin'

  function manejarCerrarSesion() {
    cerrarSesion()
    navigate('/')
  }

  return (
    <header className="border-bottom bg-white sticky-top ts-no-imprimir">
      <nav className="navbar navbar-expand-lg container py-2">
        <Link to="/" className="navbar-brand d-flex align-items-center gap-2">
          <span className="ts-logo-badge">
            <i className="bi bi-geo-alt-fill"></i>
          </span>
          <span className="ts-brand-text fw-bold">
            TuriSmart <span className="ts-text-primary">Lima</span>
          </span>
        </Link>

        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#turismartNav"
          aria-controls="turismartNav"
          aria-expanded="false"
          aria-label="Abrir menú"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        <div className="collapse navbar-collapse" id="turismartNav">
          <ul className="navbar-nav mx-lg-auto my-3 my-lg-0 gap-lg-2">
            {esAdmin ? (
              <>
                <li className="nav-item">
                  <NavLink to="/admin/lugares" end className={navLinkClass}>
                    <i className="bi bi-speedometer2"></i> Panel administrativo
                  </NavLink>
                </li>
                <li className="nav-item">
                  <Link to="/admin/lugares#admin-agregar" className="nav-link-ts d-flex align-items-center gap-2 px-3 py-2 rounded-pill">
                    <i className="bi bi-plus-circle"></i> Agregar lugar
                  </Link>
                </li>
                <li className="nav-item">
                  <Link to="/admin/lugares#admin-catalogo" className="nav-link-ts d-flex align-items-center gap-2 px-3 py-2 rounded-pill">
                    <i className="bi bi-pencil-square"></i> Editar y eliminar
                  </Link>
                </li>
              </>
            ) : (
              <>
                <li className="nav-item">
                  <NavLink to="/explorar" id="tour-explorar" className={navLinkClass}>
                    <i className="bi bi-geo-alt"></i> Explorar
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink to="/mapa" id="tour-mapa" className={navLinkClass}>
                    <i className="bi bi-map"></i> Mapa GIS
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink to="/itinerario" className={navLinkClass}>
                    <i className="bi bi-clipboard-check"></i> Mi Itinerario
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink to="/dashboard" className={navLinkClass}>
                    <i className="bi bi-bar-chart-line"></i> Dashboard
                  </NavLink>
                </li>
              </>
            )}
          </ul>

          <div className="d-flex align-items-center gap-3 mt-3 mt-lg-0">
            {!esAdmin && (
              <Link to="/planificar" className="btn btn-ts-primary rounded-pill px-3">
                Planifica tu viaje
              </Link>
            )}

            {autenticado ? (
              <div className="d-flex align-items-center gap-2">
                <span className="ts-user-icon" id="tour-cuenta" aria-hidden="true">
                  <i className="bi bi-person-fill"></i>
                </span>
                <span className="small fw-semibold text-truncate" style={{ maxWidth: '120px' }}>
                  {usuario.nombre.split(' ')[0]}
                </span>
                {esAdmin && <span className="badge ts-badge-admin">Admin</span>}
                <button
                  type="button"
                  className="btn btn-sm btn-light border"
                  onClick={manejarCerrarSesion}
                  aria-label="Cerrar sesión"
                  title="Cerrar sesión"
                >
                  <i className="bi bi-box-arrow-right"></i>
                </button>
              </div>
            ) : (
              <Link to="/login" className="btn btn-ts-outline rounded-pill d-flex align-items-center gap-2 px-3">
                <i className="bi bi-person"></i>
                <span>Ingresar</span>
              </Link>
            )}
          </div>
        </div>
      </nav>
    </header>
  )
}

export default Navbar
