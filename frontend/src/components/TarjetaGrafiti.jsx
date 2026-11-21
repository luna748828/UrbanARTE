import { useState } from "react";
import { useAuth } from "../auth.jsx";
import { editarPublicacion, eliminarPublicacion } from "../api.js";
import Ventana from "./Ventana.jsx";

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
  const [confirmandoBorrar, setConfirmandoBorrar] = useState(false);
  const [eliminando, setEliminando] = useState(false);
  const [yoLoHice, setYoLoHice] = useState(!!obra.artista_propio);
  const [error, setError] = useState("");
  const [guardando, setGuardando] = useState(false);

  const puedeEditar = !!onCambio && !!usuario && obra.usuario_id === usuario.id;
  const puedeBorrar = !!onBorrar && !!usuario && (obra.usuario_id === usuario.id || usuario.rol === "administrador");

  async function guardar(e) {
    e.preventDefault();
    const datos = new FormData(e.target);

    const desc = (datos.get("descripcion") || "").trim();
    if (!desc) {
      setError("Escribe una descripción o título.");
      return;
    }
    if (desc.length < 3 || desc.length > 1000) {
      setError(`La descripción debe tener entre 3 y 1000 caracteres (tienes ${desc.length}).`);
      return;
    }

    const archivo = datos.get("imagen_archivo");
    if (archivo && archivo.size > 0) {
      const permitidos = ["image/jpeg", "image/png", "image/webp"];
      if (!permitidos.includes(archivo.type)) {
        setError("Formato no válido. Usa JPG, PNG o WEBP.");
        return;
      }
      if (archivo.size > 5 * 1024 * 1024) {
        setError("La imagen no puede pesar más de 5 MB.");
        return;
      }
    }

    setGuardando(true);
    setError("");
    try {
      await editarPublicacion(obra.id, datos);
      setEditando(false);
      onCambio();
    } catch (err) {
      setError(err.message);
    }
    setGuardando(false);
  }

  async function ejecutarBorrado() {
    setEliminando(true);
    setError("");
    try {
      await eliminarPublicacion(obra.id);
      setConfirmandoBorrar(false);
      if (onCambio) onCambio();
    } catch (err) {
      setError(err.message);
      setConfirmandoBorrar(false);
    }
    setEliminando(false);
  }

  const u = obra.usuarios;
  const subidoPor = u?.nombre_usuario || obra.nombre_usuario;
  const artista = (obra.artista || "").replace(/^@/, "");

  return (
    <>
      <article className="tarjeta">
        <div className="foto-wrap">
          <div className={"foto-cuadro " + FONDOS[indice % FONDOS.length]}>
            {obra.imagen ? <img src={obra.imagen} alt={obra.descripcion || "grafiti"} loading="lazy" /> : <b>sin foto</b>}
          </div>
        </div>

        {editando ? (
          <form className="info" onSubmit={guardar} noValidate>
            <label>Descripción o título
              <input name="descripcion" defaultValue={obra.descripcion} maxLength={1000} />
            </label>
            <label>Tipo
              <select name="categoria" defaultValue={obra.categoria || "GRAFITI"}>
                <option>GRAFITI</option><option>STENCIL</option><option>MURAL</option>
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
              <label>Artista (nombre, sin @)
                <input name="artista" maxLength={60} defaultValue={artista} placeholder="ej: Botero" />
              </label>
            )}
            <label>Barrio o dirección
              <input name="direccion" defaultValue={obra.direccion_aprox || ""} />
            </label>
            <label>Cambiar la foto (JPG, PNG, WEBP - máx. 5 MB)
              <input type="file" name="imagen_archivo" accept="image/jpeg,image/png,image/webp" />
            </label>

            {error && (
              <div
                style={{
                  margin: "8px 0",
                  padding: "8px 10px",
                  border: "2px solid var(--pink)",
                  background: "rgba(18, 12, 36, 0.92)",
                  color: "var(--pink)",
                }}
              >
                [!] {error}
              </div>
            )}

            <div>
              <button className="btn" type="submit" disabled={guardando}>
                {guardando ? "Guardando..." : "Guardar"}
              </button>
              <button className="btn" type="button" onClick={() => { setEditando(false); setError(""); }}>
                Cancelar
              </button>
            </div>
          </form>
        ) : (
          <div className="info">
            <div className="dato tipo"><span className="simbolo">#</span>{obra.categoria || "GRAFITI"}</div>

            {obra.artista_propio && subidoPor ? (
              <div className="dato artista"><Avatar usuario={u} /><span>@{subidoPor}</span></div>
            ) : (
              <div className="dato artista"><IconoPaleta /><span>{artista || "artista desconocido"}</span></div>
            )}

            <p className="desc">{obra.descripcion}</p>
            <div className="dato ubi"><IconoPin />{obra.direccion_aprox || "sin ubicación"}</div>
            {!obra.artista_propio && subidoPor && (
              <div className="muted subido"><Avatar usuario={u} tam={22} /> subido por @{subidoPor}</div>
            )}

            {error && (
              <div
                style={{
                  margin: "8px 0",
                  padding: "8px 10px",
                  border: "2px solid var(--pink)",
                  background: "rgba(18, 12, 36, 0.92)",
                  color: "var(--pink)",
                }}
              >
                [!] {error}
              </div>
            )}

            {(puedeEditar || puedeBorrar) && (
              <div>
                {puedeEditar && (
                  <button className="btn" onClick={() => { setYoLoHice(!!obra.artista_propio); setEditando(true); }}>
                    Editar
                  </button>
                )}
                {puedeBorrar && (
                  <button className="btn" onClick={() => setConfirmandoBorrar(true)}>
                    Eliminar
                  </button>
                )}
              </div>
            )}
          </div>
        )}
      </article>

      {confirmandoBorrar && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(10, 6, 22, 0.78)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 9999,
            padding: 16,
          }}
        >
          <div style={{ width: "100%", maxWidth: 400 }}>
            <Ventana titulo="eliminar_obra.exe">
              <p style={{ margin: "6px 0 16px", lineHeight: 1.4 }}>
                ¿Eliminar esta publicación de forma permanente?
              </p>
              <div style={{ display: "flex", gap: 10, justifyContent: "flex-end" }}>
                <button
                  type="button"
                  className="btn"
                  disabled={eliminando}
                  onClick={() => setConfirmandoBorrar(false)}
                >
                  Cancelar
                </button>
                <button
                  type="button"
                  className="btn"
                  disabled={eliminando}
                  style={{ borderColor: "var(--pink)", color: "var(--pink)" }}
                  onClick={ejecutarBorrado}
                >
                  {eliminando ? "Eliminando..." : "Eliminar"}
                </button>
              </div>
            </Ventana>
          </div>
        </div>
      )}
    </>
  );
}