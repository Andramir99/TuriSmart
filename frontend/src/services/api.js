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
    throw new ApiError('No se pudo conectar con el servidor. ¿Está corriendo el backend?', 0)
  }

  const tipoContenido = respuesta.headers.get('content-type') || ''
  const datos = tipoContenido.includes('application/json') ? await respuesta.json() : null

  if (!respuesta.ok) {
    throw new ApiError(extraerMensaje(datos), respuesta.status, datos)
  }

  return datos
}
