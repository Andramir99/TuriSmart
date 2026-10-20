// Punto único de comunicación con el backend. Ningún componente llama a
// fetch() directamente: todos pasan por aquí, así que si mañana cambia
// la URL base, el formato de errores, o cómo se manda el token, se
// arregla en un solo lugar.
const URL_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export class ApiError extends Error {
  constructor(mensaje, status, detalle) {
    super(mensaje)
    this.name = 'ApiError'
    this.status = status
    this.detalle = detalle
  }
}

// FastAPI devuelve los errores de validación (422) como una LISTA de
// objetos {msg, loc, ...}, no como un texto simple. Esta función arma un
// mensaje legible sin importar cuál de las dos formas vino.
function extraerMensaje(datos) {
  const detalle = datos?.detail
  if (typeof detalle === 'string') return detalle
  if (Array.isArray(detalle)) return detalle.map((item) => item.msg).join('. ')
  return 'Ocurrió un error al comunicarse con el servidor.'
}

// Algunas respuestas (ej. 204 No Content, como DELETE /itinerarios/{id})
// vienen con el cuerpo vacío pero IGUAL con el header
// "Content-Type: application/json" — confiar en ese header y llamar
// directo a response.json() revienta con un SyntaxError porque no hay
// nada que parsear. Por eso se lee como texto primero, y solo se
// intenta convertir a JSON si de verdad hay contenido.
async function leerCuerpoJSON(respuesta) {
  const texto = await respuesta.text()
  if (!texto) return null
  try {
    return JSON.parse(texto)
  } catch {
    return null
  }
}

export async function solicitar(ruta, { metodo = 'GET', cuerpo, token } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers.Authorization = `Bearer ${token}`

  let respuesta
  try {
    respuesta = await fetch(`${URL_BASE}${ruta}`, {
      method: metodo,
      headers,
      body: cuerpo !== undefined ? JSON.stringify(cuerpo) : undefined,
    })
  } catch {
    throw new ApiError(
      'El servicio no está disponible en este momento. Verifica tu conexión a internet e inténtalo nuevamente en unos minutos.',
      0
    )
  }

  const datos = await leerCuerpoJSON(respuesta)

  if (!respuesta.ok) {
    throw new ApiError(extraerMensaje(datos), respuesta.status, datos)
  }

  return datos
}
