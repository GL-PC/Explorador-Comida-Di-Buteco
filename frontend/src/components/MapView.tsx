// MAP COMPONENT

import { MapContainer, TileLayer } from 'react-leaflet'

export default function MapView() {
  const initCoord: [number, number] = [-19.916681, -43.934493]

  return (
    <div className="w-full h-full overflow-hidden rounded-2xl flex">
      <MapContainer
      worldCopyJump={true}
      attributionControl={false}
        center={initCoord}
        zoom={7}
        scrollWheelZoom={true}
        className="h-full w-full rounded-2x"
      >
        <TileLayer
          attribution="© Gustavo and Pedro "
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />
      </MapContainer>
    </div>
  )
}