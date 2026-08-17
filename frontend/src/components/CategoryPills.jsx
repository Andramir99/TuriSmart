// Fila de píldoras de categoría (Todos, Cultural, Natural, ...).
// Es un componente "controlado": no guarda su propio estado, recibe la
// categoría activa y avisa al padre cuando el usuario elige otra.
function CategoryPills({ categorias, activa, onCambiar }) {
  return (
    <div className="d-flex flex-wrap gap-2">
      {categorias.map((categoria) => (
        <button
          key={categoria.slug}
          type="button"
          className={`ts-pill${activa === categoria.slug ? ' ts-pill--active' : ''}`}
          onClick={() => onCambiar(categoria.slug)}
        >
          {categoria.label}
        </button>
      ))}
    </div>
  )
}

export default CategoryPills
