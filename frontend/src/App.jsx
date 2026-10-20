import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import Footer from './components/Footer.jsx'
import RutaPrivada from './components/RutaPrivada.jsx'
import RutaAdmin from './components/RutaAdmin.jsx'
import Home from './pages/Home.jsx'
import Explorar from './pages/Explorar.jsx'
import DestinoDetalle from './pages/DestinoDetalle.jsx'
import MapaGIS from './pages/MapaGIS.jsx'
import MiItinerario from './pages/MiItinerario.jsx'
import ItinerarioDetalle from './pages/ItinerarioDetalle.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Planificar from './pages/Planificar.jsx'
import Login from './pages/Login.jsx'
import Privacidad from './pages/Privacidad.jsx'
import AdminLugares from './pages/AdminLugares.jsx'
import PageNotFound from './pages/PageNotFound.jsx'

function App() {
  return (
    <div className="d-flex flex-column min-vh-100">
      <Navbar />

      <main className="flex-grow-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/explorar" element={<Explorar />} />
          <Route path="/explorar/:id" element={<DestinoDetalle />} />
          <Route path="/mapa" element={<MapaGIS />} />
          <Route
            path="/itinerario"
            element={
              <RutaPrivada>
                <MiItinerario />
              </RutaPrivada>
            }
          />
          <Route
            path="/itinerario/:id"
            element={
              <RutaPrivada>
                <ItinerarioDetalle />
              </RutaPrivada>
            }
          />
          <Route
            path="/dashboard"
            element={
              <RutaPrivada>
                <Dashboard />
              </RutaPrivada>
            }
          />
          <Route path="/planificar" element={<Planificar />} />
          <Route path="/login" element={<Login />} />
          <Route
            path="/admin/lugares"
            element={
              <RutaAdmin>
                <AdminLugares />
              </RutaAdmin>
            }
          />
          <Route path="/privacidad" element={<Privacidad />} />
          <Route path="*" element={<PageNotFound />} />
        </Routes>
      </main>

      <Footer />
    </div>
  )
}

export default App
