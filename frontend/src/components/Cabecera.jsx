export default function Cabecera() {
  return (
    <header>
      <div className="hero">
        <div className="px" style={{ fontSize: 9, color: "var(--lilac)" }}>♥ ♥ ♥ bienvenid@ a ♥ ♥ ♥</div>
        <h1 className="logo">UrbanARTE</h1>
        <div className="sub">el arte sale a la calle</div>
        <div className="floor" aria-hidden="true" />
      </div>
      <div className="mq"><span>✦ nuevos grafitis cada día ✦ jam de muralistas el sábado ✦ sube tu obra y deja tu firma ✦</span></div>
    </header>
  );
}