import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import * as authService from '../services/authService.js'

const AuthContext = createContext(null)
const CLAVE_TOKEN = 'turismart_token'
// Igual mecanismo que CLAVE_TOKEN, pero para la guía de bienvenida
// (GuiaBienvenida.jsx): se marca solo al crear una cuenta nueva, nunca al
// iniciar sesión en una ya existente, y se borra apenas el usuario ve o
// salta el tour — así no vuelve a aparecer.
export const CLAVE_TOUR_PENDIENTE = 'turismart_tour_pendiente'

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(CLAVE_TOKEN))
  const [usuario, setUsuario] = useState(null)
  // "cargando" evita que, al recargar la página, por un instante se vea
  // la app como si nadie hubiera iniciado sesión mientras se confirma el
  // token guardado contra el backend.
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    if (!token) {
      setUsuario(null)
      setCargando(false)
      return
    }

    let cancelado = false
    authService
      .obtenerPerfil(token)
      .then((datos) => {
        if (!cancelado) setUsuario(datos)
      })
      .catch(() => {
        // El token guardado ya no sirve (expiró o el usuario fue borrado).
        if (!cancelado) {
          localStorage.removeItem(CLAVE_TOKEN)
          setToken(null)
          setUsuario(null)
        }
      })
      .finally(() => {
        if (!cancelado) setCargando(false)
      })

    return () => {
      cancelado = true
    }
  }, [token])

  const iniciarSesion = useCallback(async (correo, contrasena) => {
    const { access_token: accessToken } = await authService.iniciarSesion({ correo, contrasena })
    localStorage.setItem(CLAVE_TOKEN, accessToken)
    setToken(accessToken)
  }, [])

  const registrar = useCallback(
    async (nombre, correo, contrasena) => {
      // /auth/registro y /auth/login son dos endpoints separados a
      // propósito (ver Etapa 7, backend): registrar crea la cuenta,
      // pero no abre sesión sola. Por eso, después de crearla, hacemos
      // login para obtener el token.
      await authService.registrar({ nombre, correo, contrasena })
      await iniciarSesion(correo, contrasena)
      localStorage.setItem(CLAVE_TOUR_PENDIENTE, '1')
    },
    [iniciarSesion],
  )

  const cerrarSesion = useCallback(() => {
    localStorage.removeItem(CLAVE_TOKEN)
    setToken(null)
    setUsuario(null)
  }, [])

  const value = {
    usuario,
    token,
    cargando,
    autenticado: Boolean(usuario),
    iniciarSesion,
    registrar,
    cerrarSesion,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const contexto = useContext(AuthContext)
  if (!contexto) {
    throw new Error('useAuth() debe usarse dentro de <AuthProvider>')
  }
  return contexto
}
