import { useEffect, useState } from "react";
import { getPerfil, guardarPerfil, subirFotoPerfil, getTiposArtista, cambiarClave, desactivarCuenta, getMisPublicaciones, eliminarPublicacion } from "../api.js";
import { useAuth } from "../auth.jsx";
import Ventana from "../components/Ventana.jsx";
import TarjetaGrafiti from "../components/TarjetaGrafiti.jsx";

const OTRO = "__otro__";

export default function Perfil() {
  const { setUsuario } = useAuth();
  const [perfil, setPerfil] = useState(null);
  const [tipos, setTipos] = useState([]);
  const [editando, setEditando] = useState(false);
  const [tipoSel, setTipoSel] = useState("");
  const [mensaje, setMensaje] = useState({ texto: "", error: false });
  const [aviso, setAviso] = useState({ texto: "", error: false });
  const [obras, setObras] = useState(null);

  const cargar = () => getPerfil().then(setPerfil).catch((e) => setMensaje({ texto: e.message, error: true }));
  useEffect(() => {
    cargar();
    getTiposArtista().then(setTipos).catch(() => {});
    getMisPublicaciones().then(setObras).catch(() => setObras([]));
  }, []);

  function abrirEdicion() {
    setTipoSel(perfil?.tipo_artista || "");
    setEditando(true);
  }

  async function guardar(e) {
    e.preventDefault();
    const f = new FormData(e.target);
    const tipo = tipoSel === OTRO ? (f.get("tipo_nuevo") || "").trim() : tipoSel;
    try {
      const d = await guardarPerfil(f.get("nombre_usuario"), f.get("biografia"), tipo);
      const foto = f.get("foto");
      if (foto && foto.name) {
        const fd = new FormData();
        fd.append("foto", foto);
        await subirFotoPerfil(fd);
      }
      setMensaje({ texto: d.mensaje, error: false });
      if (d.usuario) setUsuario(d.usuario);
      setEditando(false);
      cargar();
      getTiposArtista().then(setTipos).catch(() => {});
    } catch (err) {
      setMensaje({ texto: err.message, error: true });
    }
  }

  async function borrarObra(id) {
    if (!window.confirm("¿Eliminar esta publicación?")) return;
    try {
      await eliminarPublicacion(id);
      setObras((lista) => lista.filter((o) => o.id !== id));
    } catch (err) {
      setMensaje({ texto: err.message, error: true });
    }
  }

  async function nuevaClave(e) {
    e.preventDefault();
    const f = new FormData(e.target);
    try {
      const d = await cambiarClave(f.get("nueva_clave"));
      setAviso({ texto: d.mensaje, error: false });
      e.target.reset();
    } catch (err) {
      setAviso({ texto: err.message, error: true });
    }
  }

  async function desactivar(e) {
    e.preventDefault();
    if (!window.confirm("Esto elimina tu cuenta por completo. ¿Seguro?")) return;
    const f = new FormData(e.target);
    try {
      await desactivarCuenta(f.get("contrasena"));
      setUsuario(null);
    } catch (err) {
      setAviso({ texto: err.message, error: true });
    }
  }

  return (
    <>
      <Ventana titulo="perfil.usr">
        {!perfil && !mensaje.texto && <p className="muted">cargando...</p>}
        {perfil && (
          <div className="perfil-card">
            {editando ? (
              <form className="perfil-datos" onSubmit={guardar}>
                <label>Nombre de usuario<input name="nombre_usuario" defaultValue={perfil.nombre_usuario} required /></label>
                <label>Descripción<textarea name="biografia" rows="4" defaultValue={perfil.biografia || ""} /></label>
                <label>Tipo de artista
                  <select value={tipoSel} onChange={(e) => setTipoSel(e.target.value)}>
                    <option value="">sin especificar</option>
                    {tipos.map((t) => <option key={t} value={t}>{t}</option>)}
                    <option value={OTRO}>No está en la lista: agregar el mío…</option>
                  </select>
                </label>
                {tipoSel === OTRO && (
                  <label>Tu tipo de artista<input name="tipo_nuevo" maxLength="40" placeholder="por ejemplo: Ceramista" required /></label>
                )}
                <label>Foto de perfil<input type="file" name="foto" accept="image/*" /></label>
                <div>
                  <button className="btn" type="submit">Guardar</button>
                  <button className="btn" type="button" onClick={() => setEditando(false)}>Cancelar</button>
                </div>
              </form>
            ) : (
              <div className="perfil-datos">
                <div className="dato artista"><span className="simbolo">@</span>{perfil.nombre_usuario}</div>
                <div className="dato correo">{perfil.correo}</div>
                <p className="desc">{perfil.biografia || "Aún no has escrito tu descripción."}</p>
                <div className="dato tipo"><span className="simbolo">#</span>{perfil.tipo_artista || "sin tipo de artista"}</div>
                <div><button className="btn" onClick={abrirEdicion}>Editar perfil</button></div>
              </div>
            )}
            <div className="perfil-foto">
              {perfil.foto_url ? (
                <img src={perfil.foto_url} alt="foto de perfil" />
              ) : (
                <span>{(perfil.nombre_usuario || "?")[0].toUpperCase()}</span>
              )}
            </div>
          </div>
        )}
        {mensaje.texto && <p style={{ color: mensaje.error ? "var(--pink)" : "var(--green)" }}>{mensaje.texto}</p>}
      </Ventana>

      <Ventana titulo="mis_obras.exe">
        {obras === null && <p className="muted">cargando...</p>}
        {obras && obras.length === 0 && <p className="muted">Aún no has subido ninguna obra.</p>}
        {(obras || []).map((o, i) => <TarjetaGrafiti key={o.id} obra={o} indice={i} onBorrar={borrarObra} onCambio={() => getMisPublicaciones().then(setObras)} />)}
      </Ventana>

      <Ventana titulo="cuenta.cfg">
        <form onSubmit={nuevaClave}>
          <label>Nueva contraseña<input type="password" name="nueva_clave" required placeholder="mínimo 8, un número y un símbolo" /></label>
          <button className="btn" type="submit">Cambiar contraseña</button>
        </form>
        <hr style={{ border: 0, borderTop: "1px dashed var(--lilac)", margin: "16px 0" }} />
        <form onSubmit={desactivar}>
          <p className="muted">Eliminar tu cuenta es definitivo. Escribe tu contraseña para confirmar.</p>
          <label>Contraseña actual<input type="password" name="contrasena" required /></label>
          <button className="btn" type="submit" style={{ borderColor: "var(--pink)" }}>Eliminar mi cuenta</button>
        </form>
        {aviso.texto && <p style={{ color: aviso.error ? "var(--pink)" : "var(--green)" }}>{aviso.texto}</p>}
      </Ventana>
    </>
  );
}