import { useState } from "react";
import { MapContainer, TileLayer, Marker, useMapEvents, useMap } from "react-leaflet";
import { crearPublicacion } from "../api.js";
import Ventana from "../components/Ventana.jsx";

function ClickEnMapa({ onElegir }) {
  useMapEvents({ click: (e) => onElegir(e.latlng.lat, e.latlng.lng) });
  return null;
}
function Centrar({ punto }) {
  const mapa = useMap();
  if (punto) mapa.setView(punto, 16);
  return null;
}

export default function Publicar() {
  const [punto, setPunto] = useState(null); // [lat, lng]
  const [direccion, setDireccion] = useState("");
  const [vista, setVista] = useState(null);
  const [estado, setEstado] = useState({ texto: "", error: false });
  const [enviando, setEnviando] = useState(false);

  async function elegir(lat, lng) {
    setPunto([lat, lng]);
    try {
      const r = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`);
      const d = await r.json();
      const a = d.address || {};
      setDireccion(a.suburb || a.neighbourhood || a.road || d.display_name || "");
    } catch {
      /* si falla, la persona puede escribir el barrio */
    }
  }

  function usarMiUbicacion() {
    navigator.geolocation?.getCurrentPosition(
      (p) => elegir(p.coords.latitude, p.coords.longitude),
      () => setEstado({ texto: "No se pudo obtener tu ubicación. Toca el mapa.", error: true })
    );
  }

  async function enviar(e) {
    e.preventDefault();
    const datos = new FormData(e.target);
    if (punto) {
      datos.set("lat", punto[0]);
      datos.set("lng", punto[1]);
    }
    datos.set("direccion", direccion);
    setEnviando(true);
    try {
      const d = await crearPublicacion(datos);
      setEstado({ texto: d.mensaje || "Publicado", error: false });
      e.target.reset();
      setVista(null);
      setPunto(null);
      setDireccion("");
    } catch (err) {
      setEstado({ texto: err.message, error: true });
    }
    setEnviando(false);
  }

  return (
    <Ventana titulo="publicar_obra.exe">
      <form onSubmit={enviar}>
        <label>Descripción o título<input name="descripcion" required /></label>
        <label>Tipo
          <select name="categoria"><option>GRAFITI</option><option>STENCIL</option><option>MURAL</option></select>
        </label>
        <label>Artista (quién lo hizo, si lo sabes)<input name="artista" placeholder="@nombre" /></label>
        <label>Foto desde tu dispositivo
          <input type="file" name="imagen_archivo" accept="image/*"
            onChange={(e) => setVista(e.target.files[0] ? URL.createObjectURL(e.target.files[0]) : null)} />
        </label>
        {vista && <img src={vista} alt="vista previa" style={{ maxWidth: 220, border: "2px solid var(--lilac)", marginBottom: 10 }} />}
        <label>Link de imagen (opcional)<input name="imagen" placeholder="https://..." /></label>

        <p style={{ margin: "6px 0" }}>Dónde está (toca el mapa)</p>
        <button type="button" className="btn" onClick={usarMiUbicacion}>Usar mi ubicación</button>
        <div className="mapa-real" style={{ marginTop: 8 }}>
          <MapContainer center={[4.62, -74.08]} zoom={12} style={{ height: 260 }}>
            <TileLayer attribution="&copy; OpenStreetMap" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            <ClickEnMapa onElegir={elegir} />
            <Centrar punto={punto} />
            {punto && <Marker position={punto} />}
          </MapContainer>
        </div>
        <label style={{ display: "block", marginTop: 8 }}>Barrio o dirección
          <input value={direccion} onChange={(e) => setDireccion(e.target.value)} />
        </label>

        <button className="btn" type="submit" disabled={enviando}>{enviando ? "Subiendo..." : "Publicar"}</button>
        {estado.texto && <p style={{ color: estado.error ? "var(--pink)" : "var(--green)" }}>{estado.texto}</p>}
      </form>
    </Ventana>
  );
}