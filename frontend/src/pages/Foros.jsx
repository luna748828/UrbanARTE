import { useEffect, useState } from "react";
import { getForos, getForo, crearTema, getTema, responder, editarTema, eliminarTema, editarRespuesta, eliminarRespuesta } from "../api.js";
import { useAuth } from "../auth.jsx";
import Ventana from "../components/Ventana.jsx";

const autorDe = (x) => x?.autor || x?.nombre_usuario || x?.usuarios?.nombre_usuario || "";
const fechaDe = (x) => {
  const f = x?.fecha || x?.creado_en || x?.fecha_foro;
  return f ? new Date(f).toLocaleDateString("es-CO") : "";
};

export default function Foros() {
  const [foroId, setForoId] = useState(null);
  const [temaId, setTemaId] = useState(null);

  if (foroId && temaId) return <VistaTema foroId={foroId} temaId={temaId} volver={() => setTemaId(null)} />;
  if (foroId) return <VistaForo foroId={foroId} abrirTema={setTemaId} volver={() => setForoId(null)} />;
  return <ListaForos abrir={setForoId} />;
}

function ListaForos({ abrir }) {
  const [foros, setForos] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => { getForos().then(setForos).catch((e) => setError(e.message)); }, []);

  return (
    <Ventana titulo="foros.bbs">
      {error && <p style={{ color: "var(--pink)" }}>{error}</p>}
      {foros && foros.length === 0 && <p className="muted">No hay foros todavía.</p>}
      {(foros || []).map((f) => (
        <div className="row" key={f.id}>
          <button className="btn" onClick={() => abrir(f.id)}>{f.nombre || f.titulo || f.tema_foro || "Foro " + f.id}</button>
          {f.descripcion && <div className="muted">{f.descripcion}</div>}
        </div>
      ))}
    </Ventana>
  );
}

function VistaForo({ foroId, abrirTema, volver }) {
  const [datos, setDatos] = useState(null);
  const [mensaje, setMensaje] = useState({ texto: "", error: false });

  const cargar = () => getForo(foroId).then(setDatos).catch((e) => setMensaje({ texto: e.message, error: true }));
  useEffect(() => { cargar(); }, [foroId]);

  async function nuevoTema(e) {
    e.preventDefault();
    const f = new FormData(e.target);
    try {
      const d = await crearTema(foroId, f.get("titulo"), f.get("contenido"));
      e.target.reset();
      setMensaje({ texto: d.mensaje, error: false });
      if (d.tema_id) abrirTema(d.tema_id); else cargar();
    } catch (err) {
      setMensaje({ texto: err.message, error: true });
    }
  }

  const foro = datos?.foro;
  return (
    <>
      <Ventana titulo={"foro: " + (foro?.nombre || foro?.titulo || foro?.tema_foro || "...")}>
        <button className="btn" onClick={volver}>← Foros</button>
        {foro?.descripcion && <p className="muted">{foro.descripcion}</p>}
        {(datos?.temas || []).map((t) => (
          <div className="row" key={t.id}>
            <button className="btn" onClick={() => abrirTema(t.id)}>{t.titulo}</button>
            <div className="muted">{autorDe(t) && "por @" + autorDe(t)} {fechaDe(t)}</div>
          </div>
        ))}
        {datos && datos.temas?.length === 0 && <p className="muted">Todavía no hay temas. ¡Crea el primero!</p>}
      </Ventana>
      <Ventana titulo="nuevo_tema.exe">
        <form onSubmit={nuevoTema}>
          <label>Título<input name="titulo" required /></label>
          <label>Mensaje<textarea name="contenido" rows="4" required /></label>
          <button className="btn" type="submit">Publicar tema</button>
          {mensaje.texto && <p style={{ color: mensaje.error ? "var(--pink)" : "var(--green)" }}>{mensaje.texto}</p>}
        </form>
      </Ventana>
    </>
  );
}

function VistaTema({ foroId, temaId, volver }) {
  const { usuario } = useAuth();
  const [tema, setTema] = useState(null);
  const [mensaje, setMensaje] = useState({ texto: "", error: false });
  const [editandoTema, setEditandoTema] = useState(false);
  const [editandoResp, setEditandoResp] = useState(null);

  const cargar = () => getTema(foroId, temaId).then(setTema).catch((e) => setMensaje({ texto: e.message, error: true }));
  useEffect(() => { cargar(); }, [temaId]);

  // Los botones solo aparecen en lo propio; el servidor igual verifica que sea de quien edita.
  const esMio = (x) => !!usuario && (x?.usuario_id === usuario.id || autorDe(x) === usuario.nombre_usuario);

  async function intentar(accion, despues) {
    try {
      const d = await accion();
      setMensaje({ texto: d?.mensaje || "", error: false });
      despues?.();
    } catch (err) {
      setMensaje({ texto: err.message, error: true });
    }
  }

  async function enviar(e) {
    e.preventDefault();
    const f = new FormData(e.target);
    await intentar(() => responder(foroId, temaId, f.get("contenido")), () => { e.target.reset(); cargar(); });
  }

  function guardarTema(e) {
    e.preventDefault();
    const f = new FormData(e.target);
    intentar(() => editarTema(foroId, temaId, f.get("titulo"), f.get("contenido")), () => { setEditandoTema(false); cargar(); });
  }

  function borrarTema() {
    if (!window.confirm("¿Borrar este tema?")) return;
    intentar(() => eliminarTema(foroId, temaId), volver);
  }

  function guardarResp(e, id) {
    e.preventDefault();
    const f = new FormData(e.target);
    intentar(() => editarRespuesta(foroId, temaId, id, f.get("contenido")), () => { setEditandoResp(null); cargar(); });
  }

  function borrarResp(id) {
    if (!window.confirm("¿Borrar esta respuesta?")) return;
    intentar(() => eliminarRespuesta(foroId, temaId, id), cargar);
  }

  return (
    <>
      <Ventana titulo={"tema: " + (tema?.titulo || "...")}>
        <button className="btn" onClick={volver}>← Volver al foro</button>
        {tema && !editandoTema && (
          <>
            <p className="muted">{autorDe(tema) && "por @" + autorDe(tema)} {fechaDe(tema)}</p>
            <p style={{ whiteSpace: "pre-wrap" }}>{tema.contenido}</p>
            {esMio(tema) && (
              <div>
                <button className="btn" onClick={() => setEditandoTema(true)}>Editar</button>
                <button className="btn" onClick={borrarTema}>Borrar</button>
              </div>
            )}
          </>
        )}
        {tema && editandoTema && (
          <form onSubmit={guardarTema}>
            <label>Título<input name="titulo" defaultValue={tema.titulo} required /></label>
            <label>Mensaje<textarea name="contenido" rows="4" defaultValue={tema.contenido} required /></label>
            <button className="btn" type="submit">Guardar</button>
            <button className="btn" type="button" onClick={() => setEditandoTema(false)}>Cancelar</button>
          </form>
        )}

        {(tema?.respuestas || []).map((r) => (
          <div className="row" key={r.id}>
            <div className="muted">{autorDe(r) && "@" + autorDe(r)} {fechaDe(r)}</div>
            {editandoResp === r.id ? (
              <form onSubmit={(e) => guardarResp(e, r.id)}>
                <textarea name="contenido" rows="3" defaultValue={r.contenido} required />
                <button className="btn" type="submit">Guardar</button>
                <button className="btn" type="button" onClick={() => setEditandoResp(null)}>Cancelar</button>
              </form>
            ) : (
              <>
                <div style={{ whiteSpace: "pre-wrap" }}>{r.contenido}</div>
                {esMio(r) && (
                  <div style={{ marginTop: 6 }}>
                    <button className="btn" onClick={() => setEditandoResp(r.id)}>Editar</button>
                    <button className="btn" onClick={() => borrarResp(r.id)}>Borrar</button>
                  </div>
                )}
              </>
            )}
          </div>
        ))}
        {mensaje.texto && <p style={{ color: mensaje.error ? "var(--pink)" : "var(--green)" }}>{mensaje.texto}</p>}
      </Ventana>
      <Ventana titulo="responder.exe">
        <form onSubmit={enviar}>
          <label>Tu respuesta<textarea name="contenido" rows="3" required /></label>
          <button className="btn" type="submit">Responder</button>
        </form>
      </Ventana>
    </>
  );
}