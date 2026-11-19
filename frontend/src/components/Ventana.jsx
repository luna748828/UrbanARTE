// Caja con barra de título estilo ventana antigua. Se usa en todas las pantallas.
export default function Ventana({ titulo, children }) {
  return (
    <section className="win">
      <div className="bar"><span>{titulo}</span><i>_ □ x</i></div>
      <div className="body">{children}</div>
    </section>
  );
}
