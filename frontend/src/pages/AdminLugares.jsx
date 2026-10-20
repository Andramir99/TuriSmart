import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { ApiError } from '../services/api.js'
import { obtenerCategorias } from '../services/categoriasService.js'
import { actualizarLugar, crearLugar, eliminarLugar, obtenerLugares } from '../services/lugaresService.js'
import '../styles/wizard.css'

const FORM_VACIO = {
  nombre: '',
  descripcion: '',
  descripcion_corta: '',
  categoria_id: '',
  distrito: '',
  direccion: '',
  precio: '',
  horario: '',
  duracion_estimada_min: '',
  tipo_turismo: '',
  nivel_popularidad: 3,
  servicios_disponibles: '',
  recomendaciones_visitante: '',
  lat: '',
  lon: '',
  accesible_movilidad_reducida: false,
  imagen_url: '',
  etiquetas: '',
  fuente_informacion: '',
}

// El backend guarda listas (etiquetas, servicios_disponibles) como
// arrays; en el formulario se editan como texto separado por comas,
// más simple que armar un selector de chips para un panel interno.
function listaATexto(lista) {
  return Array.isArray(lista) ? lista.join(', ') : ''
}

function textoALista(texto) {
  const partes = texto
    .split(',')
    .map((parte) => parte.trim())
    .filter(Boolean)
  return partes.length ? partes : null
}

function lugarAFormulario(lugar) {
  return {
    nombre: lugar.nombre,
    descripcion: lugar.descripcion || '',
    descripcion_corta: lugar.descripcion_corta || '',
    categoria_id: String(lugar.categoria.id),
    distrito: lugar.distrito,
    direccion: lugar.direccion || '',
    precio: lugar.precio ?? '',
    horario: lugar.horario || '',
    duracion_estimada_min: lugar.duracion_estimada_min ?? '',
    tipo_turismo: lugar.tipo_turismo || '',
    nivel_popularidad: lugar.nivel_popularidad,
    servicios_disponibles: listaATexto(lugar.servicios_disponibles),
    recomendaciones_visitante: lugar.recomendaciones_visitante || '',
    lat: lugar.lat,
    lon: lugar.lon,
    accesible_movilidad_reducida: lugar.accesible_movilidad_reducida,
    imagen_url: lugar.imagen_url || '',
    etiquetas: listaATexto(lugar.etiquetas),
    fuente_informacion: lugar.fuente_informacion || '',
  }
}

function formularioACuerpo(form) {
  return {
    nombre: form.nombre.trim(),
    descripcion: form.descripcion.trim() || null,
    descripcion_corta: form.descripcion_corta.trim() || null,
    categoria_id: Number(form.categoria_id),
    distrito: form.distrito.trim(),
    direccion: form.direccion.trim() || null,
    precio: form.precio === '' ? null : Number(form.precio),
    horario: form.horario.trim() || null,
    duracion_estimada_min: form.duracion_estimada_min === '' ? null : Number(form.duracion_estimada_min),
    tipo_turismo: form.tipo_turismo.trim() || null,
    nivel_popularidad: Number(form.nivel_popularidad),
    servicios_disponibles: textoALista(form.servicios_disponibles),
    recomendaciones_visitante: form.recomendaciones_visitante.trim() || null,
    lat: Number(form.lat),
    lon: Number(form.lon),
    accesible_movilidad_reducida: form.accesible_movilidad_reducida,
    imagen_url: form.imagen_url.trim() || null,
    etiquetas: textoALista(form.etiquetas),
    fuente_informacion: form.fuente_informacion.trim() || null,
  }
}

function AdminLugares() {
  const { usuario, token } = useAuth()
  const ubicacion = useLocation()

  const [categorias, setCategorias] = useState([])
  const [lugares, setLugares] = useState([])
  const [cargando, setCargando] = useState(true)
  const [form, setForm] = useState(FORM_VACIO)
  const [editandoId, setEditandoId] = useState(null)
  const [enviando, setEnviando] = useState(false)
  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')

  async function cargarLugares() {
    const datos = await obtenerLugares()
    setLugares(datos)
  }

  useEffect(() => {
    Promise.all([obtenerCategorias(), obtenerLugares()])
      .then(([listaCategorias, listaLugares]) => {
        setCategorias(listaCategorias)
        setLugares(listaLugares)
        setForm((actual) => ({ ...actual, categoria_id: String(listaCategorias[0]?.id || '') }))
      })
      .catch(() => setError('No se pudo cargar el catálogo. Intenta recargar la página.'))
      .finally(() => setCargando(false))
  }, [])

  function actualizarCampo(campo, valor) {
    setForm((actual) => ({ ...actual, [campo]: valor }))
  }

  function empezarEdicion(lugar) {
    setEditandoId(lugar.id)
    setForm(lugarAFormulario(lugar))
    setMensaje('')
    setError('')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  function cancelarEdicion() {
    setEditandoId(null)
    setForm((actual) => ({ ...FORM_VACIO, categoria_id: actual.categoria_id }))
  }

  // El navbar de administrador enlaza directo a #admin-agregar y
  // #admin-catalogo (dos secciones de esta misma página, no rutas
  // distintas). "Agregar lugar" además limpia cualquier edición en
  // curso, para que de verdad abra un formulario en blanco.
  useEffect(() => {
    if (!ubicacion.hash || cargando) return

    if (ubicacion.hash === '#admin-agregar' && editandoId) {
      cancelarEdicion()
    }

    const elemento = document.querySelector(ubicacion.hash)
    elemento?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ubicacion.hash, cargando])

  async function manejarSubmit(evento) {
    evento.preventDefault()
    setError('')
    setMensaje('')
    setEnviando(true)
    try {
      const cuerpo = formularioACuerpo(form)
      if (editandoId) {
        await actualizarLugar(editandoId, cuerpo, token)
        setMensaje(`"${cuerpo.nombre}" se actualizó correctamente.`)
      } else {
        await crearLugar(cuerpo, token)
        setMensaje(`"${cuerpo.nombre}" se agregó al catálogo.`)
      }
      setEditandoId(null)
      setForm((actual) => ({ ...FORM_VACIO, categoria_id: actual.categoria_id }))
      await cargarLugares()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo conectar con el servidor.')
    } finally {
      setEnviando(false)
    }
  }

  async function manejarEliminar(lugar) {
    if (!window.confirm(`¿Quitar "${lugar.nombre}" del catálogo? Dejará de verse en Explorar y el Mapa.`)) return
    setError('')
    setMensaje('')
    try {
      await eliminarLugar(lugar.id, token)
      setMensaje(`"${lugar.nombre}" se quitó del catálogo.`)
      if (editandoId === lugar.id) cancelarEdicion()
      await cargarLugares()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo conectar con el servidor.')
    }
  }

  if (cargando) {
    return (
      <div className="container py-5 text-center text-muted">
        <span className="spinner-border spinner-border-sm me-2"></span>
        Cargando panel...
      </div>
    )
  }

  return (
    <div className="container py-5">
      <p className="ts-eyebrow mb-1">Panel de administración</p>
      <h1 className="ts-heading mb-2">Catálogo de lugares</h1>
      <p className="text-muted mb-4">
        Hola, {usuario.nombre.split(' ')[0]}. Desde acá agregas, editas o quitas atractivos del catálogo que
        ve toda la plataforma.
      </p>

      {error && (
        <div className="alert alert-danger small py-2" role="alert">
          <i className="bi bi-exclamation-circle me-1"></i>
          {error}
        </div>
      )}
      {mensaje && (
        <div className="alert alert-success small py-2" role="status">
          <i className="bi bi-check-circle me-1"></i>
          {mensaje}
        </div>
      )}

      <div className="row g-4">
        <div className="col-lg-5" id="admin-agregar" style={{ scrollMarginTop: '90px' }}>
          <div className="ts-wizard-card">
            <h2 className="h5 fw-bold mb-3">{editandoId ? 'Editar lugar' : 'Agregar lugar nuevo'}</h2>

            <form onSubmit={manejarSubmit} noValidate>
              <div className="mb-3">
                <label className="form-label fw-semibold">Nombre</label>
                <input
                  type="text"
                  className="form-control"
                  value={form.nombre}
                  onChange={(e) => actualizarCampo('nombre', e.target.value)}
                  required
                  minLength={3}
                />
              </div>

              <div className="row g-2 mb-3">
                <div className="col-6">
                  <label className="form-label fw-semibold">Categoría</label>
                  <select
                    className="form-select"
                    value={form.categoria_id}
                    onChange={(e) => actualizarCampo('categoria_id', e.target.value)}
                    required
                  >
                    {categorias.map((cat) => (
                      <option key={cat.id} value={cat.id}>
                        {cat.nombre}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="col-6">
                  <label className="form-label fw-semibold">Distrito</label>
                  <input
                    type="text"
                    className="form-control"
                    value={form.distrito}
                    onChange={(e) => actualizarCampo('distrito', e.target.value)}
                    required
                    minLength={2}
                  />
                </div>
              </div>

              <div className="mb-3">
                <label className="form-label fw-semibold">Descripción corta</label>
                <input
                  type="text"
                  className="form-control"
                  maxLength={200}
                  value={form.descripcion_corta}
                  onChange={(e) => actualizarCampo('descripcion_corta', e.target.value)}
                />
              </div>

              <div className="mb-3">
                <label className="form-label fw-semibold">Descripción completa</label>
                <textarea
                  className="form-control"
                  rows={3}
                  value={form.descripcion}
                  onChange={(e) => actualizarCampo('descripcion', e.target.value)}
                />
              </div>

              <div className="row g-2 mb-3">
                <div className="col-6">
                  <label className="form-label fw-semibold">Latitud</label>
                  <input
                    type="number"
                    step="any"
                    className="form-control"
                    value={form.lat}
                    onChange={(e) => actualizarCampo('lat', e.target.value)}
                    required
                  />
                </div>
                <div className="col-6">
                  <label className="form-label fw-semibold">Longitud</label>
                  <input
                    type="number"
                    step="any"
                    className="form-control"
                    value={form.lon}
                    onChange={(e) => actualizarCampo('lon', e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="row g-2 mb-3">
                <div className="col-6">
                  <label className="form-label fw-semibold">Dirección</label>
                  <input
                    type="text"
                    className="form-control"
                    value={form.direccion}
                    onChange={(e) => actualizarCampo('direccion', e.target.value)}
                  />
                </div>
                <div className="col-6">
                  <label className="form-label fw-semibold">Horario</label>
                  <input
                    type="text"
                    className="form-control"
                    value={form.horario}
                    onChange={(e) => actualizarCampo('horario', e.target.value)}
                    placeholder="9:00 am - 5:00 pm"
                  />
                </div>
              </div>

              <div className="row g-2 mb-3">
                <div className="col-4">
                  <label className="form-label fw-semibold">Precio (S/)</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    className="form-control"
                    value={form.precio}
                    onChange={(e) => actualizarCampo('precio', e.target.value)}
                  />
                </div>
                <div className="col-4">
                  <label className="form-label fw-semibold">Duración (min)</label>
                  <input
                    type="number"
                    min="0"
                    className="form-control"
                    value={form.duracion_estimada_min}
                    onChange={(e) => actualizarCampo('duracion_estimada_min', e.target.value)}
                  />
                </div>
                <div className="col-4">
                  <label className="form-label fw-semibold">Popularidad</label>
                  <select
                    className="form-select"
                    value={form.nivel_popularidad}
                    onChange={(e) => actualizarCampo('nivel_popularidad', e.target.value)}
                  >
                    {[1, 2, 3, 4, 5].map((n) => (
                      <option key={n} value={n}>
                        {n}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="mb-3">
                <label className="form-label fw-semibold">Tipo de turismo</label>
                <input
                  type="text"
                  className="form-control"
                  value={form.tipo_turismo}
                  onChange={(e) => actualizarCampo('tipo_turismo', e.target.value)}
                  placeholder="Museos y otros"
                />
              </div>

              <div className="mb-3">
                <label className="form-label fw-semibold">URL de imagen</label>
                <input
                  type="url"
                  className="form-control"
                  value={form.imagen_url}
                  onChange={(e) => actualizarCampo('imagen_url', e.target.value)}
                  placeholder="https://..."
                />
              </div>

              <div className="mb-3">
                <label className="form-label fw-semibold">Etiquetas (separadas por coma)</label>
                <input
                  type="text"
                  className="form-control"
                  value={form.etiquetas}
                  onChange={(e) => actualizarCampo('etiquetas', e.target.value)}
                  placeholder="familiar, al aire libre, fotografía"
                />
              </div>

              <div className="mb-3">
                <label className="form-label fw-semibold">Servicios disponibles (separados por coma)</label>
                <input
                  type="text"
                  className="form-control"
                  value={form.servicios_disponibles}
                  onChange={(e) => actualizarCampo('servicios_disponibles', e.target.value)}
                  placeholder="estacionamiento, guías, baños"
                />
              </div>

              <div className="mb-3">
                <label className="form-label fw-semibold">Recomendación para el visitante</label>
                <textarea
                  className="form-control"
                  rows={2}
                  value={form.recomendaciones_visitante}
                  onChange={(e) => actualizarCampo('recomendaciones_visitante', e.target.value)}
                />
              </div>

              <div className="mb-3">
                <label className="form-label fw-semibold">Fuente de la información</label>
                <input
                  type="text"
                  className="form-control"
                  value={form.fuente_informacion}
                  onChange={(e) => actualizarCampo('fuente_informacion', e.target.value)}
                  placeholder="MINCETUR/SIGMINCETUR"
                />
              </div>

              <div className="form-check mb-3">
                <input
                  type="checkbox"
                  className="form-check-input"
                  id="accesible"
                  checked={form.accesible_movilidad_reducida}
                  onChange={(e) => actualizarCampo('accesible_movilidad_reducida', e.target.checked)}
                />
                <label className="form-check-label" htmlFor="accesible">
                  Accesible para movilidad reducida
                </label>
              </div>

              <div className="d-flex gap-2">
                <button type="submit" className="btn btn-ts-primary flex-grow-1" disabled={enviando}>
                  {enviando ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                      Guardando...
                    </>
                  ) : editandoId ? (
                    'Guardar cambios'
                  ) : (
                    'Agregar lugar'
                  )}
                </button>
                {editandoId && (
                  <button type="button" className="btn btn-light border" onClick={cancelarEdicion}>
                    Cancelar
                  </button>
                )}
              </div>
            </form>
          </div>
        </div>

        <div className="col-lg-7" id="admin-catalogo" style={{ scrollMarginTop: '90px' }}>
          <h2 className="h5 fw-bold mb-3">Lugares en el catálogo ({lugares.length})</h2>
          <div className="d-flex flex-column gap-2">
            {lugares.map((lugar) => (
              <div
                key={lugar.id}
                className="ts-wizard-card d-flex justify-content-between align-items-center gap-3 py-3"
              >
                <div>
                  <p className="fw-semibold mb-0">{lugar.nombre}</p>
                  <p className="small text-muted mb-0">
                    {lugar.categoria.nombre} · {lugar.distrito}
                  </p>
                </div>
                <div className="d-flex gap-2 flex-shrink-0">
                  <button
                    type="button"
                    className="btn btn-sm btn-light border"
                    onClick={() => empezarEdicion(lugar)}
                    aria-label={`Editar ${lugar.nombre}`}
                  >
                    <i className="bi bi-pencil"></i>
                  </button>
                  <button
                    type="button"
                    className="btn btn-sm btn-light border text-danger"
                    onClick={() => manejarEliminar(lugar)}
                    aria-label={`Quitar ${lugar.nombre}`}
                  >
                    <i className="bi bi-trash"></i>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default AdminLugares
