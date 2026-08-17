// Catálogo de categorías turísticas y su presentación visual (colores de
// las etiquetas). Es configuración de interfaz, no datos de negocio, por
// eso vive junto a los componentes y no en src/data/.
export const CATEGORIAS = [
  { slug: 'todos', label: 'Todos' },
  { slug: 'cultural', label: 'Cultural' },
  { slug: 'natural', label: 'Natural' },
  { slug: 'gastronomico', label: 'Gastronómico' },
  { slug: 'aventura', label: 'Aventura' },
  { slug: 'arqueologico', label: 'Arqueológico' },
]

const BADGE_CLASS_BY_CATEGORIA = {
  cultural: 'ts-badge--cultural',
  natural: 'ts-badge--natural',
  gastronomico: 'ts-badge--gastronomico',
  aventura: 'ts-badge--aventura',
  arqueologico: 'ts-badge--arqueologico',
}

export function claseBadgeCategoria(slug) {
  return BADGE_CLASS_BY_CATEGORIA[slug] || 'ts-badge--cultural'
}

export function etiquetaCategoria(slug) {
  const encontrada = CATEGORIAS.find((categoria) => categoria.slug === slug)
  return encontrada ? encontrada.label : slug
}
