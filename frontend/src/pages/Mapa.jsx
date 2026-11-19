import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import { getPublicaciones, getEventos } from "../api.js";
import Ventana from "../components/Ventana.jsx";

// Pin en forma de gota con la foto del grafiti dentro.
// Si hay varias obras en el mismo lugar, muestra el número.
function iconoPin({ evento, n, pasado, imagen }) {
  const limpia = (imagen || "").replace(/["'()\s]/g, "");
  const interior =
    n > 1
      ? `<div class="num">${n}</div>`
      : `<div class="foto${evento ? " ev" : ""}" style="${limpia ? `background-image:url(${limpia});background-size:cover;background-position:center` : ""}"></div>`;
  return L.divIcon({
    className: "pin-wrap",
    html: `<div class="pin${pasado ? " pasado" : ""}"><div class="sombra"></div><div class="gota${evento ? " ev" : ""}">${interior}</div></div>`,
    iconSize: [44, 58],
    iconAnchor: [22, 54],
  });
}

// Un solo pin por lugar: se agrupa lo que esté a ~100 m (3 decimales).
function agrupar(items) {
  const grupos = {};
  items.forEach((it) => {
    const k = Number(it.latitud).toFixed(3) + "," + Number(it.longitud).toFixed(3);
    (grupos[k] = grupos[k] || { lat: Number(it.latitud), lng: Number(it.longitud), items: [] }).items.push(it);
  });
  return Object.values(grupos);
}

// Mapa con filtros. Se usa en la pestaña Mapa (grande) y en el Inicio (pequeño).
export function MapaPanel({ obras, eventos, alto = 440 }) {
  const [vista, setVista] = useState("todo"); // todo | grafitis | eventos
  const [artista, setArtista] = useState("");

  const artistas = [...new Set(obras.map((o) => o.artista).filter(Boolean))];
  const ahora = new Date();
  const puntos = [];
  if (vista !== "eventos") {
    obras
      .filter((o) => o.latitud != null && (!artista || o.artista === artista))
      .forEach((o) => puntos.push({ ...o, tipo: "grafiti" }));
  }
  if (vista !== "grafitis" && !artista) {
    eventos
      .filter((e) => e.latitud != null)
      .forEach((e) => puntos.push({ ...e, tipo: "evento", pasado: new Date(e.fecha_hora) < ahora }));
  }

  return (
    <>
      <div className="mapa-real">
        <MapContainer center={[4.62, -74.08]} zoom={12} style={{ height: alto }}>
          <TileLayer attribution="&copy; OpenStreetMap" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          {agrupar(puntos).map((g) => {
            const evento = g.items.every((i) => i.tipo === "evento");
            const pasado = g.items.every((i) => i.pasado);
            const imagen = g.items.find((i) => i.imagen)?.imagen;
            return (
              <Marker key={g.lat + "," + g.lng} position={[g.lat, g.lng]} icon={iconoPin({ evento, n: g.items.length, pasado, imagen })}>
                <Popup>
                  {g.items.map((i) => (
                    <div key={i.tipo + i.id} style={{ marginBottom: 8 }}>
                      {i.imagen && <img src={i.imagen} alt="" style={{ width: 160, display: "block" }} />}
                      <b>{i.descripcion || i.nombre}</b>
                      <div>
                        {i.tipo === "evento"
                          ? i.pasado ? "Evento ya ocurrido" : "Próximo evento"
                          : i.artista ? "Artista: " + i.artista : ""}
                      </div>
                    </div>
                  ))}
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </div>
      <div style={{ marginTop: 10 }}>
        {[["todo", "Todo"], ["grafitis", "Grafitis"], ["eventos", "Eventos"]].map(([v, t]) => (
          <button key={v} className={"btn" + (vista === v ? " on" : "")} onClick={() => setVista(v)}>{t}</button>
        ))}
      </div>
      <label style={{ display: "block", marginTop: 10 }}>Artista
        <select value={artista} onChange={(e) => setArtista(e.target.value)}>
          <option value="">todos los artistas</option>
          {artistas.map((a) => <option key={a}>{a}</option>)}
        </select>
      </label>
      <p className="muted" style={{ margin: 0 }}>Un pin por lugar; si hay varios, se agrupan con número. Lila: evento. Apagado: evento que ya pasó.</p>
    </>
  );
}

export default function Mapa() {
  const [obras, setObras] = useState([]);
  const [eventos, setEventos] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getPublicaciones().then(setObras).catch((e) => setError(e.message));
    getEventos().then(setEventos).catch((e) => setError(e.message));
  }, []);

  return (
    <Ventana titulo="mapa_de_grafitis.map">
      {error && <p style={{ color: "var(--pink)" }}>{error}</p>}
      <MapaPanel obras={obras} eventos={eventos} alto={460} />
    </Ventana>
  );
}