// Opciones de "tipo de viajero" del Paso 1 del wizard. Corresponden a lo
// que en el backend será la tabla "categorias" (Etapa 6): cada una tiene
// un id/slug, nombre y descripción. Por ahora son fijas en el frontend;
// en la Etapa 8 este archivo se reemplaza por GET /categorias.
const tiposViajeroMock = [
  {
    slug: 'cultura',
    nombre: 'Cultura & Historia',
    descripcion: 'Museos, plazas y arquitectura colonial',
    icono: 'bi-bank',
  },
  {
    slug: 'naturaleza',
    nombre: 'Naturaleza',
    descripcion: 'Lomas, parques y costa verde',
    icono: 'bi-tree',
  },
  {
    slug: 'gastronomia',
    nombre: 'Gastronomía',
    descripcion: 'Ceviches, mercados y chefs estrella',
    icono: 'bi-egg-fried',
  },
  {
    slug: 'aventura',
    nombre: 'Aventura',
    descripcion: 'Senderismo, surf y deportes extremos',
    icono: 'bi-compass',
  },
  {
    slug: 'relax',
    nombre: 'Relax',
    descripcion: 'Playas, spas y parques tranquilos',
    icono: 'bi-water',
  },
  {
    slug: 'nocturno',
    nombre: 'Nocturno',
    descripcion: 'Bares, clubs y vida nocturna limeña',
    icono: 'bi-moon-stars',
  },
]

export default tiposViajeroMock
