import { solicitar } from './api.js'

export function registrar({ nombre, correo, contrasena }) {
  return solicitar('/auth/registro', { metodo: 'POST', cuerpo: { nombre, correo, contrasena } })
}

export function iniciarSesion({ correo, contrasena }) {
  return solicitar('/auth/login', { metodo: 'POST', cuerpo: { correo, contrasena } })
}

export function obtenerPerfil(token) {
  return solicitar('/usuarios/me', { token })
}

export function actualizarPerfil(datos, token) {
  return solicitar('/usuarios/me', { metodo: 'PUT', cuerpo: datos, token })
}

export function solicitarRestablecimiento(correo) {
  return solicitar('/auth/olvide-contrasena', { metodo: 'POST', cuerpo: { correo } })
}

export function restablecerContrasena(token, nuevaContrasena) {
  return solicitar('/auth/restablecer-contrasena', {
    metodo: 'POST',
    cuerpo: { token, nueva_contrasena: nuevaContrasena },
  })
}
