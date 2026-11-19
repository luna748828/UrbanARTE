const FONDOS = ["p1", "p2", "p3"];

function IconoPin() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" aria-hidden="true">
      <path d="M12 22s7-6.5 7-12a7 7 0 1 0-14 0c0 5.5 7 12 7 12z" />
      <circle cx="12" cy="10" r="2.5" />
    </svg>
  );
}

// Foto cuadrada a la izquierda; a la derecha: # tipo, @ artista, descripción y ubicación.
export default function TarjetaGrafiti({ obra, indice = 0 }) {
  const subidoPor = obra.usuarios?.nombre_usuario || obra.nombre_usuario;
  const artista = (obra.artista || "").replace(/^@/, "");
  return (
    <article className="tarjeta">
      <div className="foto-wrap">
        <div className={"foto-cuadro " + FONDOS[indice % FONDOS.length]}>
          {obra.imagen ? <img src={obra.imagen} alt={obra.descripcion || "grafiti"} loading="lazy" /> : <b>sin foto</b>}
        </div>
      </div>
      <div className="info">
        <div className="dato tipo"><span className="simbolo">#</span>{obra.categoria || "GRAFITI"}</div>
        <div className="dato artista"><span className="simbolo">@</span>{artista || "artista sin nombre"}</div>
        <p className="desc">{obra.descripcion}</p>
        <div className="dato ubi"><IconoPin />{obra.direccion_aprox || "sin ubicación"}</div>
        {subidoPor && <div className="muted subido">subido por @{subidoPor}</div>}
      </div>
    </article>
  );
}