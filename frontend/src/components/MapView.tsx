import {Circle,LayerGroup,MapContainer,Marker, Popup ,TileLayer,useMap,} from "react-leaflet";
import { useEffect } from "react";
import L from "leaflet";
import pinIconUrl from "../assets/pin.png";
import searchPinIconUrl from "../assets/search-pin.png";


export type MapMarkerBar = {
  id: string | number;
  nome: string;
  endereco: string;
  bairro?: string;
  cidade?: string;
  rua?: string;
  numero?: string;
  estado?: string;
  lat: number;
  lng: number;
  imagemPratoUrl?: string;
};

type MapViewProps = {
  markers: MapMarkerBar[];
  coordenadasBusca: Coordenadas | null;
  raioBuscaKm: number;
};

type Coordenadas = {
  lat: number;
  lng: number;
};

const barIcon = L.icon({
  iconUrl: pinIconUrl,
  iconSize: [44, 44],
  iconAnchor: [22, 44],
  popupAnchor: [0, -40],
  tooltipAnchor: [0, -33],
});

const searchIcon = L.icon({
  iconUrl: searchPinIconUrl,
  iconSize: [48, 48],
  iconAnchor: [24, 48],
  popupAnchor: [0, -44],
  tooltipAnchor: [0, -36],
});


function FlyToSearchLocation({
  coordenadasBusca,
  raioBuscaKm,
}: {
  coordenadasBusca: Coordenadas | null;
  raioBuscaKm: number;
}) {
  const map = useMap();

  useEffect(() => {
    if (!coordenadasBusca) return;

    const zoomPorRaio =
      raioBuscaKm <= 1
        ? 15
        : raioBuscaKm <= 3
          ? 14
          : raioBuscaKm <= 7
            ? 13
            : raioBuscaKm <= 15
              ? 12
              : 11;

    map.flyTo([coordenadasBusca.lat, coordenadasBusca.lng], zoomPorRaio, {
      duration: 1.2,
    });
  }, [coordenadasBusca, raioBuscaKm, map]);

  return null;
}
 

export default function MapView({ markers,coordenadasBusca,raioBuscaKm, }: MapViewProps) {
  const initCoord: [number, number] = [-19.916681, -43.934493];

  return (
    <div className="h-full w-full overflow-hidden rounded-2xl ">
      <MapContainer
        worldCopyJump={true}
        attributionControl={false}
        center={initCoord}
        zoom={5}
        scrollWheelZoom={true}
        className="h-full w-full rounded-2xl "
      >
        <TileLayer
          attribution="© Gustavo and Pedro"
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />

        <FlyToSearchLocation
          coordenadasBusca={coordenadasBusca}
          raioBuscaKm={raioBuscaKm}
        />

        {coordenadasBusca && raioBuscaKm > 0 && (
          <Circle
            center={[coordenadasBusca.lat, coordenadasBusca.lng]}
            radius={raioBuscaKm * 1000}
            pathOptions={{
              color: "#fc802d",
              fillColor: "#fc802d",
              fillOpacity: 0.12,
              weight: 2,
            }}
          />
        )}

        {coordenadasBusca && (
          <Marker
            position={[coordenadasBusca.lat, coordenadasBusca.lng]}
            icon={searchIcon}
          >
            <Popup>
              <div className="rounded-[14px] border-t-4 border-[#144a11] bg-white px-4 py-[14px] font-sans">
                <div className="mb-2 text-center text-[15px] font-extrabold leading-tight text-[#1f2937]">
                  Endereço buscado
                </div>

                <div className="text-center text-[12px] leading-[1.35] text-[#4b5563]">
                  Centro da busca
                </div>

                <div className="mt-1 text-center text-[11px] font-semibold text-[#6b7280]">
                  Raio: {raioBuscaKm} km
                </div>
              </div>
            </Popup>
          </Marker>
        )}

        <LayerGroup>
          {markers.map((bar) => (
            <Marker
              key={bar.id}
              position={[bar.lat, bar.lng]}
              icon={barIcon}
            >
              <Popup>
                <div className="rounded-[14px] border-t-4 border-[#fc802d] bg-white px-4 py-[14px] font-sans">
                  <div className="mb-2 text-center text-[15px] font-extrabold leading-tight text-[#1f2937]">
                    {bar.nome}
                  </div>

                  <div className="mb-2 flex justify-center">
                    <img
                      src={
                        bar.imagemPratoUrl 
                      }
                      alt={`Prato do ${bar.nome}`}
                      className="h-24 w-full rounded-lg object-cover"
                    />
                  </div>

                  <div className="mb-1.5 text-center text-[12px] leading-[1.35] text-[#4b5563]">
                    {bar.endereco && bar.endereco.trim() !== ""
                      ? bar.endereco
                      : "Endereço não informado"}
                  </div>

                  {(bar.bairro || bar.cidade) && (
                    <div className="text-center text-[11px] font-semibold text-[#6b7280]">
                      {[bar.bairro, bar.cidade].filter(Boolean).join(" • ")}
                    </div>
                  )}
                </div>
              </Popup>
            </Marker>
          ))}
        </LayerGroup>
      </MapContainer>
    </div>
  );
}