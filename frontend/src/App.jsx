import { useState } from "react";
import { useAuth } from "./auth.jsx";
import Cabecera from "./components/Cabecera.jsx";
import NavPestanas from "./components/NavPestanas.jsx";
import Acceso from "./pages/Acceso.jsx";
import Inicio from "./pages/Inicio.jsx";
import Mapa from "./pages/Mapa.jsx";
import Eventos from "./pages/Eventos.jsx";
import Foros from "./pages/Foros.jsx";
import Publicar from "./pages/Publicar.jsx";
import Perfil from "./pages/Perfil.jsx";

const PAGINAS = { Inicio, Mapa, Eventos, Foros, Publicar, Perfil };

export default function App() {
  const { usuario, salir } = useAuth();
  const [pagina, setPagina] = useState("Inicio");
  const Pagina = PAGINAS[pagina];

  return (
    <div className="page">
      <div className="wrap">
        <div className="tape"><span>ZONA LIBRE DE ARTE ★ NO BORRAR ★ ZONA LIBRE DE ARTE ★ NO BORRAR ★ ZONA LIBRE DE ARTE</span></div>
        <Cabecera />
        {usuario === undefined ? (
          <p className="muted">cargando...</p>
        ) : usuario === null ? (
          <Acceso />
        ) : (
          <>
            <NavPestanas actual={pagina} onCambiar={setPagina} onSalir={salir} nombre={usuario.nombre_usuario} />
            <main><Pagina /></main>
          </>
        )}
        <div className="cnt">VISITANTES 000142</div>
        <p className="muted" style={{ textAlign: "center", margin: 0 }}>UrbanARTE · hecho con React y mucho spray</p>
      </div>
    </div>
  );
}