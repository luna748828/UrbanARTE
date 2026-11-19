import { useEffect, useState } from "react";
import { getPerfil, guardarPerfil } from "../api.js";
import { useAuth } from "../auth.jsx";
import Ventana from "../components/Ventana.jsx";

export default function Perfil() {
  const { setUsuario } = useAuth();
  const [perfil, setPerfil] = useState(null);
  const [mensaje, setMensaje] = useState({ texto: "", error: false });

  useEffect(() => {
    getPerfil().then(setPerfil).catch((e) => setMensaje({ texto: e.message, error: true }));
  }, []);

  async function guardar(e) {
    e.preventDefault();
    const f = new FormData(e.target);
    try {
      const d = await guardarPerfil(f.get("nombre_usuario"), f.get("biografia"));
      setMensaje({ texto: d.mensaje, error: false });
      if (d.usuario) setUsuario(d.usuario);
    } catch (err) {
      setMensaje({ texto: err.message, error: true });
    }
  }

  return (
    <Ventana titulo="perfil.usr">
      {!perfil && !mensaje.texto && <p className="muted">cargando...</p>}
      {perfil && (
        <form onSubmit={guardar}>
          <div className="art p2" style={{ height: 90, marginBottom: 18 }}><b>@{perfil.nombre_usuario}</b></div>
          <p className="muted">{perfil.correo} · {perfil.rol}</p>
          <label>Nombre de usuario<input name="nombre_usuario" defaultValue={perfil.nombre_usuario} required /></label>
          <label>Biografía<textarea name="biografia" rows="4" defaultValue={perfil.biografia || ""} /></label>
          <button className="btn" type="submit">Guardar</button>
        </form>
      )}
      {mensaje.texto && <p style={{ color: mensaje.error ? "var(--pink)" : "var(--green)" }}>{mensaje.texto}</p>}
    </Ventana>
  );
}