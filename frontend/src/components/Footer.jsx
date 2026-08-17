import { Link } from 'react-router-dom'

function Footer() {
  return (
    <footer className="ts-footer pt-5 pb-3 mt-5">
      <div className="container">
        <div className="row gy-4">
          <div className="col-12 col-lg-4">
            <div className="d-flex align-items-center gap-2 mb-3">
              <span className="ts-logo-badge">
                <i className="bi bi-geo-alt-fill"></i>
              </span>
              <span className="fw-bold text-white fs-5">
                TuriSmart <span className="ts-text-primary">Lima</span>
              </span>
            </div>
            <p className="small mb-2">
              Descubre Lima de manera inteligente con IA y mapas en tiempo real.
            </p>
            <p className="small d-flex align-items-center gap-2 mb-0">
              <i className="bi bi-cpu"></i> Powered by IA &amp; GIS
            </p>
          </div>

          <div className="col-6 col-lg-2">
            <h6 className="mb-3">Explorar</h6>
            <ul className="list-unstyled d-flex flex-column gap-2 small">
              <li><Link to="/explorar">Destinos destacados</Link></li>
              <li><Link to="/mapa">Mapa interactivo</Link></li>
              <li><Link to="/explorar">Categorías</Link></li>
              <li><Link to="/explorar">Galería</Link></li>
            </ul>
          </div>

          <div className="col-6 col-lg-2">
            <h6 className="mb-3">Planifica</h6>
            <ul className="list-unstyled d-flex flex-column gap-2 small">
              <li><Link to="/planificar">Crear itinerario</Link></li>
              <li><Link to="/itinerario">Mis itinerarios</Link></li>
              <li><Link to="/planificar">Onboarding IA</Link></li>
              <li><Link to="/dashboard">Dashboard</Link></li>
            </ul>
          </div>

          <div className="col-12 col-lg-4">
            <h6 className="mb-3">Síguenos</h6>
            <div className="d-flex gap-2 mb-3">
              <a href="#" className="ts-footer-social" aria-label="Instagram">
                <i className="bi bi-instagram"></i>
              </a>
              <a href="#" className="ts-footer-social" aria-label="Twitter">
                <i className="bi bi-twitter"></i>
              </a>
              <a href="#" className="ts-footer-social" aria-label="Facebook">
                <i className="bi bi-facebook"></i>
              </a>
            </div>
            <p className="small mb-0">
              #TuriSmartLima<br />
              #DescubreLima<br />
              #PerúTurismo
            </p>
          </div>
        </div>

        <hr className="border-secondary my-4" />

        <div className="d-flex flex-column flex-md-row justify-content-between align-items-center gap-2 small">
          <span>© 2026 TuriSmart Lima. Todos los derechos reservados.</span>
          <div className="d-flex gap-3">
            <Link to="/privacidad">Privacidad</Link>
            <Link to="/terminos">Términos</Link>
            <Link to="/contacto">Contacto</Link>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer
