import { Link } from 'react-router-dom'

function PageNotFound() {
  return (
    <div className="container py-5 text-center ts-page-shell">
      <p className="ts-eyebrow mb-2">Error 404</p>
      <h1 className="ts-heading mb-3">Página no encontrada</h1>
      <p className="text-muted mb-4">La página que buscas no existe o todavía no fue creada.</p>
      <Link to="/" className="btn btn-ts-primary rounded-pill px-4">
        Volver al inicio
      </Link>
    </div>
  )
}

export default PageNotFound
