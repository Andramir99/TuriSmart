// Selector de 1 a 5 estrellas, reutilizado por la valoración de un lugar
// (DestinoDetalle) y de un itinerario (ItinerarioDetalle).
function EstrellasSelector({ valor, onCambiar, deshabilitado }) {
  return (
    <div className="d-flex gap-1">
      {[1, 2, 3, 4, 5].map((numero) => (
        <button
          key={numero}
          type="button"
          className="btn btn-sm p-0 border-0 bg-transparent"
          onClick={() => onCambiar(numero)}
          disabled={deshabilitado}
          aria-label={`${numero} estrella${numero === 1 ? '' : 's'}`}
          aria-pressed={numero === valor}
        >
          <i
            className={`bi ${numero <= valor ? 'bi-star-fill text-warning' : 'bi-star text-muted'} fs-5`}
          ></i>
        </button>
      ))}
    </div>
  )
}

export default EstrellasSelector
