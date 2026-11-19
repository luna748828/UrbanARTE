import { useEffect, useState } from "react";
import { getPublicaciones, getEventos, eliminarPublicacion } from "../api.js";
import Ventana from "../components/Ventana.jsx";
import TarjetaGrafiti from "../components/TarjetaGrafiti.jsx";
import { MapaPanel } from "./Mapa.jsx";

export default function Inicio() {
  const [obras, setObras] = useState(null);
  const [eventos, setEventos] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getPublicaciones().then(setObras).catch((e) => setError(e.message));
    getEventos().then(setEventos).catch(() => {});
  }, []);

  async function borrar(id) {
    if (!window.confirm("¿Eliminar esta publicación?")) return;
    try {
      await eliminarPublicacion(id);
      setObras((lista) => lista.filter((o) => o.id !== id));
    } catch (e) {
      setError(e.message);
    }
  }

  const ahora = new Date();
  const proximos = eventos
    .filter((e) => new Date(e.fecha_hora) >= ahora)
    .sort((a, b) => new Date(a.fecha_hora) - new Date(b.fecha_hora))
    .slice(0, 2);
  const recientes = (obras || []).slice(0, 2);

  return (
    <div className="cols">
      <div style={{ flex: "999 1 560px", minWidth: 0 }}>
        <Ventana titulo="lo_ultimo_en_la_pared.exe">
          {error && <p style={{ color: "var(--pink)" }}>{error}</p>}
          {obras === null && !error && <p className="muted">cargando...</p>}
          {obras && obras.length === 0 && <p className="muted">Aún no hay publicaciones. ¡Sube la primera desde Publicar!</p>}
          {obras && obras.map((o, i) => <TarjetaGrafiti key={o.id} obra={o} indice={i} onBorrar={borrar} onCambio={() => getPublicaciones().then(setObras)} />)}
        </Ventana>
      </div>

      <aside style={{ flex: "1 1 300px", minWidth: 0 }}>
        <Ventana titulo="mapa_de_grafitis.map">
          <MapaPanel obras={obras || []} eventos={eventos} alto={260} />
        </Ventana>

        <Ventana titulo="novedades.txt">
          {recientes.map((o) => (
            <div className="row" key={"o" + o.id}>
              <span style={{ color: "var(--pink)" }}>Nuevo:</span> {o.artista ? o.artista + " · " : ""}{o.descripcion}
            </div>
          ))}
          {proximos.map((e) => (
            <div className="row" key={"e" + e.id}>
              <span style={{ color: "var(--green)" }}>Evento:</span> {e.nombre} ·{" "}
              {new Date(e.fecha_hora).toLocaleDateString("es-CO", { day: "numeric", month: "short" })}
            </div>
          ))}
          {recientes.length === 0 && proximos.length === 0 && <p className="muted">Todavía no hay novedades.</p>}
        </Ventana>
      </aside>
    </div>
  );
}