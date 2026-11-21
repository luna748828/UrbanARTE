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
  const [yoLoHice, setYoLoHice] = useState(false);

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

  function alSeleccionarImagen(e) {
    const archivo = e.target.files[0];
    if (!archivo) {
      setVista(null);
      return;
    }

    const permitidos = ["image/jpeg", "image/png", "image/webp"];
    if (!permitidos.includes(archivo.type)) {
      setEstado({ texto: "Formato no válido. Solo se permiten JPG, PNG o WEBP.", error: true });
      e.target.value = "";
      setVista(null);
      return;
    }

    if (archivo.size > 5 * 1024 * 1024) {
      setEstado({ texto: "La imagen no puede pesar más de 5 MB.", error: true });
      e.target.value = "";
      setVista(null);
      return;
    }

    setEstado({ texto: "", error: false });
    setVista(URL.createObjectURL(archivo));
  }

  async function enviar(e) {
    e.preventDefault();
    const datos = new FormData(e.target);

    const desc = (datos.get("descripcion") || "").trim();
    if (desc.length < 3 || desc.length > 1000) {
      setEstado({ texto: "La descripción debe tener entre 3 y 1000 caracteres.", error: true });
      return;
    }

    const archivo = datos.get("imagen_archivo");
    if (archivo && archivo.size > 0) {
      const permitidos = ["image/jpeg", "image/png", "image/webp"];
      if (!permitidos.includes(archivo.type)) {
        setEstado({ texto: "Formato no válido. Usa JPG, PNG o WEBP.", error: true });
        return;
      }
      if (archivo.size > 5 * 1024 * 1024) {
        setEstado({ texto: "La imagen no puede pesar más de 5 MB.", error: true });
        return;
      }
    }

    const linkImagen = (datos.get("imagen") || "").trim();
    if (linkImagen && !/^https?:\/\/.+/i.test(linkImagen)) {
      setEstado({ texto: "El enlace de la imagen debe empezar por http:// o https://", error: true });
      return;
    }

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
      setYoLoHice(false);
    } catch (err) {
      setEstado({ texto: err.message, error: true });
    }
    setEnviando(false);
  }

  return (
    <Ventana titulo="publicar_obra.exe">
      <form onSubmit={enviar}>
        <label>Descripción o título
          <input name="descripcion" minLength={3} maxLength={1000} required />
        </label>
        <label>Tipo
          <select name="categoria">
            <option>GRAFITI</option>
            <option>STENCIL</option>
            <option>MURAL</option>
          </select>
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <input
            type="checkbox"
            name="artista_propio"
            style={{ width: "auto", margin: 0 }}
            checked={yoLoHice}
            onChange={(e) => setYoLoHice(e.target.checked)}
          />
          Yo lo hice
        </label>
        {!yoLoHice && (
          <label>Artista (nombre de quien lo hizo, sin @)
            <input name="artista" maxLength={60} placeholder="ej: Botero" />
          </label>
        )}
        <label>Foto desde tu dispositivo (JPG, PNG o WEBP - máx. 5 MB)
          <input
            type="file"
            name="imagen_archivo"
            accept="image/jpeg,image/png,image/webp"
            onChange={alSeleccionarImagen}
          />
        </label>
        {vista && (
          <img
            src={vista}
            alt="vista previa"
            style={{ maxWidth: 220, border: "2px solid var(--lilac)", marginBottom: 10 }}
          />
        )}
        <label>Link de imagen (opcional)
          <input type="url" name="imagen" placeholder="https://..." />
        </label>

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

        <button className="btn" type="submit" disabled={enviando}>
          {enviando ? "Subiendo..." : "Publicar"}
        </button>
        {estado.texto && (
          <p style={{ color: estado.error ? "var(--pink)" : "var(--green)" }}>
            {estado.texto}
          </p>
        )}
      </form>
    </Ventana>
  );
}