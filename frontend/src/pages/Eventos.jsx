import { useEffect, useState } from "react";
import { getEventos, getMisEventos, unirseAEvento, salirDeEvento, crearEvento } from "../api.js";
import { useAuth } from "../auth.jsx";
import Ventana from "../components/Ventana.jsx";
import SelectorUbicacion from "../components/SelectorUbicacion.jsx";

export default function Eventos() {
  const { usuario } = useAuth();
  const [eventos, setEventos] = useState([]);
  const [mios, setMios] = useState(new Set());
  const [mensaje, setMensaje] = useState({ texto: "", error: false });
  const [creando, setCreando] = useState(false);
  const [punto, setPunto] = useState(null);
  const [limitados, setLimitados] = useState(false);

  async function cargar() {
    try {
      setEventos(await getEventos());
      const m = await getMisEventos();
      setMios(new Set((Array.isArray(m) ? m : []).map((e) => e.id ?? e.evento_id)));
    } catch (e) {
      setMensaje({ texto: e.message, error: true });
    }
  }
  useEffect(() => { cargar(); }, []);

  async function accion(fn, id) {
    try {
      const d = await fn(id);
      setMensaje({ texto: d.mensaje || "Listo", error: false });
    } catch (e) {
      setMensaje({ texto: e.message, error: true });
    }
    cargar();
  }

  async function nuevoEvento(e) {
    e.preventDefault();
    const f = Object.fromEntries(new FormData(e.target));
    if (punto) {
      f.lat = String(punto[0]);
      f.lng = String(punto[1]);
    }
    try {
      const d = await crearEvento(f);
      setMensaje({ texto: d.mensaje, error: false });
      setCreando(false);
      setPunto(null);
      setLimitados(false);
      cargar();
    } catch (err) {
      setMensaje({ texto: err.message, error: true });
    }
  }

  const ahora = new Date();
  const proximos = eventos.filter((e) => new Date(e.fecha_hora) >= ahora);
  const pasados = eventos.filter((e) => new Date(e.fecha_hora) < ahora);

  const fila = (e, pasado) => (
    <div className="row" key={e.id} style={{ opacity: pasado ? 0.55 : 1 }}>
      <span className="chip k">{new Date(e.fecha_hora).toLocaleString("es-CO", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })}</span>
      <h2 style={{ fontSize: 22 }}>{e.nombre}</h2>
      {e.descripcion && <div>{e.descripcion}</div>}
      <div className="muted">
        {e.direccion_aprox}
        {e.usuarios?.nombre_usuario ? ` · organiza @${e.usuarios.nombre_usuario}` : ""}
        {e.cupos_disponibles != null ? ` · cupos: ${e.cupos_disponibles}` : " · sin límite de cupos"}
      </div>
      <div style={{ marginTop: 8 }}>
        {pasado ? (
          <span className="chip">ya ocurrió</span>
        ) : e.usuarios?.nombre_usuario && e.usuarios.nombre_usuario === usuario?.nombre_usuario ? (
          <span className="chip">tú organizas este evento</span>
        ) : mios.has(e.id) ? (
          <button className="btn" onClick={() => accion(salirDeEvento, e.id)}>Salir del evento</button>
        ) : (
          <button className="btn" disabled={e.cupos_disponibles === 0} onClick={() => accion(unirseAEvento, e.id)}>
            {e.cupos_disponibles === 0 ? "Sin cupos" : "Unirme"}
          </button>
        )}
      </div>
    </div>
  );

  return (
    <>
      {mensaje.texto && <p style={{ color: mensaje.error ? "var(--pink)" : "var(--green)" }}>{mensaje.texto}</p>}

      <Ventana titulo="nuevo_evento.exe">
        {!creando ? (
          <button className="btn" onClick={() => setCreando(true)}>+ Crear un evento</button>
        ) : (
          <form onSubmit={nuevoEvento}>
            <label>Nombre del evento<input name="nombre" maxLength="100" required /></label>
            <label>Descripción<textarea name="descripcion" rows="3" required /></label>
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
              <label style={{ flex: 1 }}>Fecha<input type="date" name="fecha" required /></label>
              <label style={{ flex: 1 }}>Hora<input type="time" name="hora" required /></label>
            </div>
            <label>Dirección aproximada (opcional)<input name="direccion" /></label>
            <label>Cupos
              <select value={limitados ? "limitados" : "ilimitados"} onChange={(e) => setLimitados(e.target.value === "limitados")}>
                <option value="ilimitados">Sin límite de cupos</option>
                <option value="limitados">Cupos limitados</option>
              </select>
            </label>
            {limitados && (
              <label>Cantidad de cupos<input type="number" name="cupos" min="1" max="10000" required /></label>
            )}
            <p style={{ margin: "6px 0" }}>Toca el mapa para marcar dónde será (opcional)</p>
            <SelectorUbicacion punto={punto} onElegir={(lat, lng) => setPunto([lat, lng])} />
            <div style={{ marginTop: 10 }}>
              <button className="btn" type="submit">Crear evento</button>
              <button className="btn" type="button" onClick={() => { setCreando(false); setPunto(null); }}>Cancelar</button>
            </div>
          </form>
        )}
      </Ventana>

      <Ventana titulo="proximos_eventos.cal">
        {proximos.length === 0 ? <p className="muted">No hay eventos próximos.</p> : proximos.map((e) => fila(e, false))}
      </Ventana>
      <Ventana titulo="eventos_pasados.cal">
        {pasados.length === 0 ? <p className="muted">Todavía no hay eventos pasados.</p> : pasados.map((e) => fila(e, true))}
      </Ventana>
    </>
  );
}
