import { useEffect } from 'react'
import { driver } from 'driver.js'
import 'driver.js/dist/driver.css'
import '../styles/guiaBienvenida.css'
import { CLAVE_TOUR_PENDIENTE } from '../context/AuthContext.jsx'

// Tour de bienvenida de 4 pasos: se dispara UNA sola vez, justo después de
// que alguien crea una cuenta nueva (ver AuthContext.registrar), nunca al
// iniciar sesión en una ya existente. Apunta a elementos reales de la Navbar
// y del hero de Home — nada de contenido de relleno.
//
// Se monta solo en Home.jsx porque es la única pantalla donde los 4
// elementos objetivo (hero + navbar) coexisten al mismo tiempo en el DOM.
function GuiaBienvenida() {
  useEffect(() => {
    if (localStorage.getItem(CLAVE_TOUR_PENDIENTE) !== '1') return

    const terminarTour = () => {
      try {
        localStorage.removeItem(CLAVE_TOUR_PENDIENTE)
      } catch {
        // si localStorage no está disponible, simplemente no se repite el
        // intento — no vale la pena romper la página por esto
      }
    }

    const tourDriver = driver({
      showProgress: true,
      nextBtnText: 'Siguiente',
      prevBtnText: 'Atrás',
      doneBtnText: 'Finalizar',
      progressText: 'Paso {{current}} de {{total}}',
      allowClose: true,
      onCloseClick: () => {
        terminarTour()
        tourDriver.destroy()
      },
      onDestroyed: terminarTour,
      steps: [
        {
          element: '#tour-planificar',
          popover: {
            title: 'Empieza por aquí',
            description:
              'Este botón te lleva al asistente de 3 pasos que arma tu itinerario personalizado con IA.',
            side: 'bottom',
          },
        },
        {
          element: '#tour-explorar',
          popover: {
            title: 'Explora el catálogo',
            description: 'Aquí están los destinos turísticos de Lima con foto real, precio y valoraciones.',
            side: 'bottom',
          },
        },
        {
          element: '#tour-mapa',
          popover: {
            title: 'Mapa GIS',
            description: 'Visualiza tu ruta día por día, y las paradas que ya visitaste.',
            side: 'bottom',
          },
        },
        {
          element: '#tour-cuenta',
          popover: {
            title: 'Tu cuenta',
            description: 'Desde aquí vuelves a tus itinerarios guardados cuando quieras.',
            side: 'left',
          },
        },
      ],
    })

    // Pequeño respiro para que la Home termine de pintar (destinos, etc.)
    // antes de calcular la posición de los recuadros.
    const idTimeout = setTimeout(() => tourDriver.drive(), 300)
    return () => clearTimeout(idTimeout)
  }, [])

  return null
}

export default GuiaBienvenida
