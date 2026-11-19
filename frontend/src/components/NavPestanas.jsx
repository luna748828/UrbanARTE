const PESTANAS = ["Inicio", "Mapa", "Eventos", "Foros", "Publicar"];

function IconoUsuario() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="square" aria-hidden="true">
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1" />
    </svg>
  );
}

export default function NavPestanas({ actual, onCambiar, onSalir, nombre }) {
  return (
    <nav className="tabs" role="tablist" aria-label="Secciones">
      {PESTANAS.map((n) => (
        <button key={n} role="tab" className="tab" aria-selected={actual === n} onClick={() => onCambiar(n)}>
          {n}
        </button>
      ))}
      <button role="tab" className="tab perfil" aria-selected={actual === "Perfil"} onClick={() => onCambiar("Perfil")}>
        <IconoUsuario />
        {nombre || "Perfil"}
      </button>
      <button className="tab" onClick={onSalir}>Salir</button>
    </nav>
  );
}
