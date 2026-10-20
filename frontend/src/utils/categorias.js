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

// Mismos colores que las etiquetas (.ts-badge--*), pero en hexadecimal:
// los marcadores del mapa se pintan con "backgroundColor" en línea, no con
// clases CSS, porque su posición ya se calcula dinámicamente en JS.
const COLOR_HEX_POR_CATEGORIA = {
  cultural: '#c1443c',
  natural: '#2e7d32',
  gastronomico: '#d9822b',
  aventura: '#3355cc',
  arqueologico: '#7b3fb8',
}

export function colorCategoria(slug) {
  return COLOR_HEX_POR_CATEGORIA[slug] || COLOR_HEX_POR_CATEGORIA.cultural
}

// Misma heurística que app/services/lugares_service.py en el backend:
// para que una búsqueda de texto libre también alimente el perfil
// dinámico (Etapa 16) aunque el usuario no haga clic en ningún resultado.
const PALABRAS_CLAVE_POR_CATEGORIA = {
  arqueologico: ['huaca', 'arqueolog', 'piramide', 'prehispan'],
  cultural: ['museo', 'histor', 'cultura', 'arte', 'iglesia', 'catedral', 'convento', 'plaza', 'colonial'],
  gastronomico: ['restaurante', 'gastronom', 'mercado', 'comida', 'chifa', 'pisco', 'ceviche'],
  aventura: ['aventura', 'surf', 'trekking', 'senderismo', 'deporte'],
  natural: ['natural', 'parque', 'lomas', 'bosque', 'humedal', 'jardin', 'playa'],
  relax: ['relax', 'tranquilo', 'spa', 'malecon'],
  nocturno: ['bar', 'noche', 'discoteca', 'nocturn'],
}

export function inferirCategoriaDesdeTexto(texto) {
  const normalizado = texto.toLowerCase()
  for (const [slug, palabras] of Object.entries(PALABRAS_CLAVE_POR_CATEGORIA)) {
    if (palabras.some((palabra) => normalizado.includes(palabra))) return slug
  }
  return null
}
