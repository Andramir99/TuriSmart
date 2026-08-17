// Datos de ejemplo (MOCK) para poder maquetar Home, Explorar y Mapa GIS
// mientras el catálogo turístico real todavía no existe en PostgreSQL.
//
// Este archivo se elimina en la Etapa 9, cuando estas pantallas empiecen a
// llamar a src/services/lugaresService.js -> GET /lugares en vez de importar
// este arreglo directamente. La forma de cada objeto ya imita los campos que
// tendrá la tabla "lugares" (id, nombre, distrito, categoría, coordenadas,
// rating, etc.) para que el cambio futuro sea solo cuestión de reemplazar
// el origen de los datos, no la forma en que los componentes los usan.
//
// lat/lon son coordenadas reales aproximadas (no inventadas): la idea es
// que cuando conectemos Leaflet de verdad en la Etapa 11, estos mismos
// valores sirvan tal cual, sin tener que volver a buscarlos.
const destinosMock = [
  {
    id: 1,
    nombre: 'Museo Larco',
    distrito: 'Pueblo Libre',
    categoria: 'cultural',
    imagen: 'https://picsum.photos/seed/museo-larco/480/360',
    rating: 4.8,
    resenas: 3240,
    lat: -12.0733,
    lon: -77.0717,
  },
  {
    id: 2,
    nombre: 'Malecón de Miraflores',
    distrito: 'Miraflores',
    categoria: 'natural',
    imagen: 'https://picsum.photos/seed/malecon-miraflores/480/360',
    rating: 4.9,
    resenas: 8640,
    lat: -12.1211,
    lon: -77.0324,
  },
  {
    id: 3,
    nombre: 'Santuario de Pachacamac',
    distrito: 'Lurín',
    categoria: 'arqueologico',
    imagen: 'https://picsum.photos/seed/pachacamac/480/360',
    rating: 4.6,
    resenas: 2150,
    lat: -12.2568,
    lon: -76.9022,
  },
  {
    id: 4,
    nombre: 'Barranco & Puente de los Suspiros',
    distrito: 'Barranco',
    categoria: 'cultural',
    imagen: 'https://picsum.photos/seed/barranco-suspiros/480/360',
    rating: 4.7,
    resenas: 4380,
    lat: -12.1494,
    lon: -77.0203,
  },
  {
    id: 5,
    nombre: 'Circuito Mágico del Agua',
    distrito: 'Cercado de Lima',
    categoria: 'cultural',
    imagen: 'https://picsum.photos/seed/circuito-magico-agua/480/360',
    rating: 4.5,
    resenas: 6720,
    lat: -12.0757,
    lon: -77.0332,
  },
  {
    id: 6,
    nombre: 'Lomas de Lúcumo',
    distrito: 'Pachacamac',
    categoria: 'natural',
    imagen: 'https://picsum.photos/seed/lomas-lucumo/480/360',
    rating: 4.6,
    resenas: 1890,
    lat: -12.335,
    lon: -76.82,
  },
  {
    id: 7,
    nombre: 'Costa Verde',
    distrito: 'Miraflores / Barranco',
    categoria: 'natural',
    imagen: 'https://picsum.photos/seed/costa-verde/480/360',
    rating: 4.2,
    resenas: 2980,
    lat: -12.135,
    lon: -77.03,
  },
  {
    id: 8,
    nombre: 'Bosque El Olivar',
    distrito: 'San Isidro',
    categoria: 'cultural',
    imagen: 'https://picsum.photos/seed/bosque-el-olivar/480/360',
    rating: 4.5,
    resenas: 3410,
    lat: -12.097,
    lon: -77.035,
  },
]

export default destinosMock
