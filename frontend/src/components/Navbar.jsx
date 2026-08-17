import { NavLink, Link } from 'react-router-dom'

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
  return (
    <header className="border-bottom bg-white sticky-top">
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
            <li className="nav-item">
              <NavLink to="/explorar" className={navLinkClass}>
                <i className="bi bi-geo-alt"></i> Explorar
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink to="/mapa" className={navLinkClass}>
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
          </ul>

          <div className="d-flex align-items-center gap-3 mt-3 mt-lg-0">
            <Link to="/planificar" className="btn btn-ts-primary rounded-pill px-3">
              Planifica tu viaje
            </Link>
            <Link to="/login" className="ts-user-icon" aria-label="Cuenta">
              <i className="bi bi-person"></i>
            </Link>
          </div>
        </div>
      </nav>
    </header>
  )
}

export default Navbar
