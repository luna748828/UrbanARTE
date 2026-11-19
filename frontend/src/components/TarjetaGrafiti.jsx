import { useState } from "react";
import { useAuth } from "../auth.jsx";
import { editarPublicacion } from "../api.js";

const FONDOS = ["p1", "p2", "p3"];

function IconoPin() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" aria-hidden="true">
      <path d="M12 22s7-6.5 7-12a7 7 0 1 0-14 0c0 5.5 7 12 7 12z" />
      <circle cx="12" cy="10" r="2.5" />
    </svg>
  );
}

function IconoPaleta() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" aria-hidden="true">
      <path d="M12 3a9 9 0 1 0 0 18c1.5 0 2-1 1.5-2-.6-1.2.2-2.5 1.5-2.5H17a4 4 0 0 0 4-4C21 6.5 17 3 12 3z" />
      <circle cx="7.5" cy="11" r="1" /><circle cx="10" cy="7.5" r="1" /><circle cx="14.5" cy="7.5" r="1" />
    </svg>
  );
}

// Foto de perfil redonda; si no hay, la inicial del usuario.
export function Avatar({ usuario, tam = 32 }) {
  const nombre = usuario?.nombre_usuario || "?";
  return (
    <span className="avatar" style={{ width: tam, height: tam, fontSize: tam * 0.5 }}>
      {usuario?.foto_url ? <img src={usuario.foto_url} alt="" /> : nombre[0].toUpperCase()}
    </span>
  );
}

// Foto cuadrada a la izquierda; a la derecha: # tipo, artista, descripción y ubicación.
export default function TarjetaGrafiti({ obra, indice = 0, onBorrar, onCambio }) {
  const { usuario } = useAuth();
  const [editando, setEditando] = useState(false);
  const [yoLoHice, setYoLoHice] = useState(!!obra.artista_propio);
  const [error, setError] = useState("");
  const [guardando, setGuardando] = useState(false);
  const puedeEditar = !!onCambio && !!usuario && obra.usuario_id === usuario.id;

  async function guardar(e) {
    e.preventDefault();
    setGuardando(true);
    setError("");
    try {
      await editarPublicacion(obra.id, new FormData(e.target));
      setEditando(false);
      onCambio();
    } catch (err) {
      setError(err.message);
    }
    setGuardando(false);
  }
  const puedeBorrar = !!onBorrar && !!usuario && (obra.usuario_id === usuario.id || usuario.rol === "administrador");
  const u = obra.usuarios;
  const subidoPor = u?.nombre_usuario || obra.nombre_usuario;
  const artista = (obra.artista || "").replace(/^@/, "");
  return (
    <article className="tarjeta">
      <div className="foto-wrap">
        <div className={"foto-cuadro " + FONDOS[indice % FONDOS.length]}>
          {obra.imagen ? <img src={obra.imagen} alt={obra.descripcion || "grafiti"} loading="lazy" /> : <b>sin foto</b>}
        </div>
      </div>
      {editando ? (
        <form className="info" onSubmit={guardar}>
          <label>Descripción o título<input name="descripcion" defaultValue={obra.descripcion} required /></label>
          <label>Tipo
            <select name="categoria" defaultValue={obra.categoria || "GRAFITI"}>
              <option>GRAFITI</option><option>STENCIL</option><option>MURAL</option>
            </select>
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <input type="checkbox" name="artista_propio" style={{ width: "auto", margin: 0 }}
              checked={yoLoHice} onChange={(e) => setYoLoHice(e.target.checked)} />
            Yo lo hice
          </label>
          {!yoLoHice && (
            <label>Artista (nombre, sin @)
              <input name="artista" maxLength="60" defaultValue={artista} placeholder="ej: Botero" />
            </label>
          )}
          <label>Barrio o dirección<input name="direccion" defaultValue={obra.direccion_aprox || ""} /></label>
          <label>Cambiar la foto (opcional)<input type="file" name="imagen_archivo" accept="image/*" /></label>
          {error && <p style={{ color: "var(--pink)", margin: 0 }}>{error}</p>}
          <div>
            <button className="btn" type="submit" disabled={guardando}>Guardar</button>
            <button className="btn" type="button" onClick={() => { setEditando(false); setError(""); }}>Cancelar</button>
          </div>
        </form>
      ) : (
      <div className="info">
        <div className="dato tipo"><span className="simbolo">#</span>{obra.categoria || "GRAFITI"}</div>

        {obra.artista_propio && subidoPor ? (
          // lo hizo quien lo subió: foto de perfil + @usuario
          <div className="dato artista"><Avatar usuario={u} /><span>@{subidoPor}</span></div>
        ) : (
          // lo hizo otra persona: solo el nombre, sin @ (ej: Botero)
          <div className="dato artista"><IconoPaleta /><span>{artista || "artista desconocido"}</span></div>
        )}

        <p className="desc">{obra.descripcion}</p>
        <div className="dato ubi"><IconoPin />{obra.direccion_aprox || "sin ubicación"}</div>
        {!obra.artista_propio && subidoPor && (
          <div className="muted subido"><Avatar usuario={u} tam={22} /> subido por @{subidoPor}</div>
        )}
        {(puedeEditar || puedeBorrar) && (
          <div>
            {puedeEditar && <button className="btn" onClick={() => { setYoLoHice(!!obra.artista_propio); setEditando(true); }}>Editar</button>}
            {puedeBorrar && <button className="btn" onClick={() => onBorrar(obra.id)}>Eliminar</button>}
          </div>
        )}
      </div>
      )}
    </article>
  );
}