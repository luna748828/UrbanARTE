import { MapContainer, TileLayer, Marker, useMapEvents } from "react-leaflet";

function Click({ onElegir }) {
  useMapEvents({ click: (e) => onElegir(e.latlng.lat, e.latlng.lng) });
  return null;
}

// Mapa donde se toca para marcar un lugar. punto = [lat, lng] o null.
export default function SelectorUbicacion({ punto, onElegir, alto = 260 }) {
  return (
    <div className="mapa-real">
      <MapContainer center={punto || [4.62, -74.08]} zoom={punto ? 15 : 12} style={{ height: alto }}>
        <TileLayer attribution="&copy; OpenStreetMap" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <Click onElegir={onElegir} />
        {punto && <Marker position={punto} />}
      </MapContainer>
    </div>
  );
}