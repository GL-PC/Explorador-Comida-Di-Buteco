import { MapContainer, TileLayer } from "react-leaflet";

export default function MapView() {
  const initCoord: [number, number] = [-19.916681, -43.934493];

  return (
    <div className="flex h-full w-full overflow-hidden rounded-2xl">
      <MapContainer
        worldCopyJump={true}
        attributionControl={false}
        center={initCoord}
        zoom={5}
        scrollWheelZoom={true}
        className="h-full w-full rounded-2xl"
      >
        <TileLayer
          attribution="© Gustavo and Pedro "
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />
      </MapContainer>
    </div>
  );
}