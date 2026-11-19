import { useState } from "react";
import { useAuth } from "../auth.jsx";
import { registro } from "../api.js";
import Ventana from "../components/Ventana.jsx";

export default function Acceso() {
  const { entrar } = useAuth();
  const [modo, setModo] = useState("login"); // login | registro
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState(false);
  const [cargando, setCargando] = useState(false);

  async function enviar(e) {
    e.preventDefault();
    const f = new FormData(e.target);
    setCargando(true);
    setMensaje("");
    try {
      if (modo === "login") {
        await entrar(f.get("correo"), f.get("contrasena"));
      } else {
        const d = await registro(f.get("nombre_usuario"), f.get("correo"), f.get("contrasena"));
        setError(false);
        setMensaje(d.mensaje);
        setModo("login");
      }
    } catch (err) {
      setError(true);
      setMensaje(err.message);
    }
    setCargando(false);
  }

  return (
    <div style={{ maxWidth: 460, margin: "24px auto" }}>
      <Ventana titulo={modo === "login" ? "entrar.exe" : "registro.exe"}>
        <form onSubmit={enviar}>
          {modo === "registro" && (
            <label>Usuario<input name="nombre_usuario" required placeholder="letras, números o _" /></label>
          )}
          <label>Correo<input name="correo" type="email" required /></label>
          <label>Contraseña<input name="contrasena" type="password" required placeholder={modo === "registro" ? "mínimo 8, un número y un símbolo" : ""} /></label>
          <button className="btn" type="submit" disabled={cargando}>{modo === "login" ? "Entrar" : "Crear cuenta"}</button>
          <button className="btn" type="button" onClick={() => { setModo(modo === "login" ? "registro" : "login"); setMensaje(""); }}>
            {modo === "login" ? "Quiero registrarme" : "Ya tengo cuenta"}
          </button>
          {mensaje && <p style={{ color: error ? "var(--pink)" : "var(--green)" }}>{mensaje}</p>}
        </form>
      </Ventana>
    </div>
  );
}