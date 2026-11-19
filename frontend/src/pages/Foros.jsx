import { useEffect, useState } from "react";
import { getForos, getForo, crearTema, getTema, responder } from "../api.js";
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
  const [tema, setTema] = useState(null);
  const [mensaje, setMensaje] = useState({ texto: "", error: false });

  const cargar = () => getTema(foroId, temaId).then(setTema).catch((e) => setMensaje({ texto: e.message, error: true }));
  useEffect(() => { cargar(); }, [temaId]);

  async function enviar(e) {
    e.preventDefault();
    const f = new FormData(e.target);
    try {
      await responder(foroId, temaId, f.get("contenido"));
      e.target.reset();
      setMensaje({ texto: "", error: false });
      cargar();
    } catch (err) {
      setMensaje({ texto: err.message, error: true });
    }
  }

  return (
    <>
      <Ventana titulo={"tema: " + (tema?.titulo || "...")}>
        <button className="btn" onClick={volver}>← Volver al foro</button>
        {tema && (
          <>
            <p className="muted">{autorDe(tema) && "por @" + autorDe(tema)} {fechaDe(tema)}</p>
            <p style={{ whiteSpace: "pre-wrap" }}>{tema.contenido}</p>
          </>
        )}
        {(tema?.respuestas || []).map((r) => (
          <div className="row" key={r.id}>
            <div className="muted">{autorDe(r) && "@" + autorDe(r)} {fechaDe(r)}</div>
            <div style={{ whiteSpace: "pre-wrap" }}>{r.contenido}</div>
          </div>
        ))}
      </Ventana>
      <Ventana titulo="responder.exe">
        <form onSubmit={enviar}>
          <label>Tu respuesta<textarea name="contenido" rows="3" required /></label>
          <button className="btn" type="submit">Responder</button>
          {mensaje.texto && <p style={{ color: mensaje.error ? "var(--pink)" : "var(--green)" }}>{mensaje.texto}</p>}
        </form>
      </Ventana>
    </>
  );
}