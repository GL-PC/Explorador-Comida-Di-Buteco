import { MapContainer, TileLayer } from 'react-leaflet'

export default function MapView() {
  const initCoord: [number, number] = [-19.916681, -43.934493]

  return (
    <div className="h-150 w-full overflow-hidden rounded-2xl shadow-lg">
      <MapContainer
        center={initCoord}
        zoom={7}
        scrollWheelZoom={true}
        className="h-full w-full"
      >
        <TileLayer
          attribution="© Gustavo and Pedro "
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />
      </MapContainer>
    </div>
  )
}