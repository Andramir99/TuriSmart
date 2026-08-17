// Componente reutilizable para las pantallas que todavía no tienen su
// diseño final del Figma. Evita repetir el mismo bloque de HTML en cada
// página de la Etapa 2. Cuando implementemos el diseño real de una página
// (Etapa 3 en adelante), esa página deja de usar este componente.
function PagePlaceholder({ eyebrow, title, description, etapa }) {
  return (
    <div className="container py-5 ts-page-shell">
      <p className="ts-eyebrow mb-2">{eyebrow}</p>
      <h1 className="ts-heading mb-3">{title}</h1>
      <p className="text-muted mb-4" style={{ maxWidth: '640px' }}>
        {description}
      </p>
      <div className="alert alert-light border d-inline-flex align-items-center gap-2">
        <i className="bi bi-tools"></i>
        <span>Esta pantalla se implementará en la {etapa}.</span>
      </div>
    </div>
  )
}

export default PagePlaceholder
