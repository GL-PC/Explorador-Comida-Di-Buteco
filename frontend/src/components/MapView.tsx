import {
  Circle,
  LayerGroup,
  MapContainer,
  Marker,
  Popup,
  TileLayer,
  useMap,
} from "react-leaflet";
import { useEffect, useRef, type MutableRefObject } from "react";
import L from "leaflet";

import pinIconUrl from "../assets/pin.png";
import searchPinIconUrl from "../assets/search-pin.png";
import type { BarResult } from "./ResultsPanel";

export type MapMarkerBar = {
  id: string | number;
  nome: string;
  endereco: string;
  bairro?: string;
  cidade?: string;
  estado?: string;
  rua?: string;
  numero?: string;
  lat: number;
  lng: number;
  imagemPratoUrl?: string;
};

type Coordenadas = {
  lat: number;
  lng: number;
};

type MapViewProps = {
  markers: MapMarkerBar[];
  coordenadasBusca: Coordenadas | null;
  raioBuscaKm: number;
  barSelecionado: BarResult | null;
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
      duration: 2.5,
    });
  }, [coordenadasBusca, raioBuscaKm, map]);

  return null;
}

function FlyToSelectedBar({
  barSelecionado,
  markerRefs,
}: {
  barSelecionado: BarResult | null;
  markerRefs: MutableRefObject<Record<string, L.Marker>>;
}) {
  const map = useMap();

  useEffect(() => {
    if (barSelecionado?.lat == null || barSelecionado?.lng == null) return;

    const zoom = 15;
    const offsetY = 140;

    const barLatLng = L.latLng(barSelecionado.lat, barSelecionado.lng);

    const pontoProjetado = map.project(barLatLng, zoom);

    const pontoComOffset = L.point(
      pontoProjetado.x,
      pontoProjetado.y - offsetY
    );

    const centroComOffset = map.unproject(pontoComOffset, zoom);

    map.flyTo(centroComOffset, zoom, {
      duration: 1,
    });

    const markerKey = String(barSelecionado.id);

    setTimeout(() => {
      markerRefs.current[markerKey]?.openPopup();
    }, 800);
  }, [barSelecionado, map, markerRefs]);

  return null;
}



export default function MapView({
  markers,
  coordenadasBusca,
  raioBuscaKm,
  barSelecionado,
}: MapViewProps) {
  const initCoord: [number, number] = [-19.916681, -43.934493];
  const markerRefs = useRef<Record<string, L.Marker>>({});

  return (
    <div className="h-full w-full overflow-hidden rounded-2xl">
      <MapContainer
        worldCopyJump={true}
        attributionControl={false}
        center={initCoord}
        zoom={5}
        scrollWheelZoom={true}
        className="h-full w-full rounded-2xl"
      >
        <TileLayer
          attribution="© Gustavo and Pedro"
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />

        <FlyToSearchLocation
          coordenadasBusca={coordenadasBusca}
          raioBuscaKm={raioBuscaKm}
        />

        <FlyToSelectedBar
          barSelecionado={barSelecionado}
          markerRefs={markerRefs}
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
              <div className="rounded-[10px] border-t-[3px] border-[#144a11] bg-white px-3 py-2 font-sans">
                <div className="mb-1 text-center text-[13px] font-extrabold leading-tight text-[#1f2937]">
                  Endereço buscado
                </div>

                <div className="text-center text-[11px] leading-[1.25] text-[#4b5563]">
                  Centro da busca
                </div>

                <div className="mt-1 text-center text-[10px] font-semibold text-[#6b7280]">
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
              ref={(marker) => {
                if (marker) {
                  markerRefs.current[String(bar.id)] = marker;
                }
              }}
            >
            <Popup>
              <div className="rounded-[14px] border-t-4 border-[#fc802d] bg-white px-4 py-[14px] font-sans">
                <div className="mb-2 text-center text-[15px] font-extrabold leading-tight text-[#1f2937]">
                  {bar.nome}
                </div>

                {bar.imagemPratoUrl && (
                  <div className="mb-2 flex justify-center">
                    <img
                      src={bar.imagemPratoUrl}
                      alt={`Prato do ${bar.nome}`}
                      className="h-24 w-full rounded-lg object-cover"
                    />
                  </div>
                )}

                <div className="mb-1 text-center text-[12px] leading-[1.35] text-[#4b5563]">
                  {[bar.rua, bar.numero].filter(Boolean).join(", ") ||
                    "Endereço não informado"}
                </div>

                {bar.bairro && (
                  <div className="mb-1 text-center text-[12px] leading-[1.35] text-[#4b5563]">
                    {bar.bairro}
                  </div>
                )}

                {(bar.cidade || bar.estado) && (
                  <div className="text-center text-[11px] font-semibold text-[#6b7280]">
                    {[bar.cidade, bar.estado].filter(Boolean).join(" - ")}
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