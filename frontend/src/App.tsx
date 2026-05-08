import { useEffect, useState } from "react";

import MapView, { type MapMarkerBar } from "./components/MapView";
import SearchForm from "./components/SearchForm";
import SearchSummary from "./components/SearchSummary";
import ResultsPanel, { type BarResult } from "./components/ResultsPanel";

import pin from "./assets/pin.png";
import home from "./assets/search-pin.png";
import mapIcon from "./assets/mapIcon.png";

import {
  getAddress,
  getButecos,
  getAllButecos,
  type ButecoMapaApi,
} from "./services/api";

type Coordenadas = {
  lat: number;
  lng: number;
};

function montarEnderecoBar(bar: ButecoMapaApi) {
  const partes = [
    bar.rua,
    bar.numero,
    bar.bairro,
    bar.cidade,
    bar.estado,
  ].filter(Boolean);

  return partes.join(", ");
}

function converterButecosParaMarkers(butecos: ButecoMapaApi[]): MapMarkerBar[] {
  return butecos
    .filter((bar) => bar.lat !== null && bar.lng !== null)
    .map((bar, index) => {
      const marker: MapMarkerBar = {
        id: `${bar.nome_do_bar}-${index}`,
        nome: bar.nome_do_bar,
        endereco: montarEnderecoBar(bar),
        bairro: bar.bairro,
        cidade: bar.cidade,
        lat: bar.lat as number,
        lng: bar.lng as number,
        imagemPratoUrl: bar.imagem_prato,
      };

      if (marker.nome.toLowerCase().includes("gisa")) {
        console.log("Objeto original da API:", bar);
        console.log("Marker convertido:", marker);
      }

      return marker;
    });
}

function converterResultadosParaMarkers(
  resultados: BarResult[]
): MapMarkerBar[] {
  return resultados
    .filter((bar) => bar.lat !== undefined && bar.lng !== undefined)
    .map((bar) => ({
      id: bar.id,
      nome: bar.nome,
      endereco: bar.endereco,
      bairro: bar.bairro,
      lat: bar.lat as number,
      lng: bar.lng as number,
      imagemPratoUrl: bar.imagemPratoUrl,
    }));
}

function App() {
  const [todosMarkers, setTodosMarkers] = useState<MapMarkerBar[]>([]);
  const [mapMarkers, setMapMarkers] = useState<MapMarkerBar[]>([]);

  const [enderecoBuscado, setEnderecoBuscado] = useState("");
  const [raioBusca, setRaioBusca] = useState(0);
  const [resultados, setResultados] = useState<BarResult[]>([]);
  const [coordenadasBusca, setCoordenadasBusca] = useState<Coordenadas | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [erroBusca, setErroBusca] = useState("");

  useEffect(() => {
    async function carregarButecosNoMapa() {
      try {
        const butecos = await getAllButecos();
        const markers = converterButecosParaMarkers(butecos);

        setTodosMarkers(markers);
        setMapMarkers(markers);
      } catch (error) {
        console.error("Erro ao carregar todos os butecos no mapa:", error);
      }
    }

    carregarButecosNoMapa();
  }, []);

  async function receberBusca(endereco: string, alcance: number) {
    try {
      setCarregando(true);
      setErroBusca("");

      setEnderecoBuscado(endereco);
      setRaioBusca(alcance);

      const coordenadas = await getAddress(endereco);
      setCoordenadasBusca(coordenadas);

      const resultadosApi = await getButecos(endereco, alcance);
      setResultados(resultadosApi);

      const markersBusca = converterResultadosParaMarkers(resultadosApi);
      setMapMarkers(markersBusca);
    } catch (error) {
      console.error(error);

      const mensagemErro =
        error instanceof Error
          ? error.message
          : "Erro inesperado ao buscar butecos.";

      setResultados([]);
      setMapMarkers([]);
      setCoordenadasBusca(null);
      setErroBusca(mensagemErro);
    } finally {
      setCarregando(false);
    }
  }

  function limparBusca() {
    setEnderecoBuscado("");
    setRaioBusca(0);
    setResultados([]);
    setCoordenadasBusca(null);
    setErroBusca("");

    setMapMarkers(todosMarkers);
  }

  function abrirPaginaDoBar(bar: BarResult) {
    window.open(bar.paginaUrl, "_blank", "noopener,noreferrer");
  }

  return (
    <main className="min-h-screen px-4 py-6 sm:px-6">
      <header className="mb-3 flex w-full flex-col items-center justify-center gap-3">
        <h1 className="text-center text-4xl font-bold text-[#144a11] sm:text-5xl">
          Explorador Comida di Buteco 2026
        </h1>

        <h2 className="text-center text-base font-normal text-black sm:text-lg">
          Encontre os bares participantes do Comida di Buteco 2026!
        </h2>
      </header>

      <div className="mx-auto mb-2 flex w-full items-center justify-center lg:w-[80%]">
        <SearchForm onBuscar={receberBusca} onLimpar={limparBusca} />
      </div>

      <div className="mx-auto mb-3 flex w-full items-center justify-center lg:w-[80%]">
        <SearchSummary
          enderecoBuscado={enderecoBuscado}
          raioBusca={raioBusca}
          quantidadeResultados={resultados.length}
        />
      </div>

      {erroBusca && (
        <div className="mx-auto mb-4 w-full rounded-xl bg-red-50 px-5 py-3 text-center font-sans text-sm font-semibold text-red-600 lg:w-[80%]">
          {erroBusca}
        </div>
      )}

      <div className="mx-auto mb-4 flex w-full flex-col gap-4 lg:h-[55vh] lg:w-[85%] lg:flex-row">
        <div className="flex h-[430px] w-full flex-col rounded-[13px] bg-white p-4 lg:h-full lg:w-[55%]">
          <div className="flex flex-col gap-3 pb-3 font-sans sm:flex-row sm:items-center sm:justify-between">
            <div className="flex">
              <div className="flex items-center justify-center gap-2 px-3">
                <img src={mapIcon} alt="Mapa" className="h-4 w-auto" />
                <p className="font-bold">Mapa de Busca</p>
              </div>
            </div>

            <div className="flex flex-col gap-2 text-gray-500 sm:flex-row sm:gap-5">
              <div className="flex items-center gap-1 px-3">
                <img
                  src={pin}
                  alt="Bares participantes"
                  className="h-5 w-auto"
                />
                <p>Bares Participantes</p>
              </div>

              <div className="flex items-center gap-1 px-3">
                <img
                  src={home}
                  alt="Endereço buscado"
                  className="h-6 w-auto"
                />
                <p>Endereço Buscado</p>
              </div>
            </div>
          </div>

          <div className="min-h-0 flex-1">
            <MapView 
            markers={mapMarkers} 
            coordenadasBusca={coordenadasBusca}
            raioBuscaKm={raioBusca}
            />
          </div>
        </div>

        <div className="h-[520px] w-full rounded-[13px] lg:h-full lg:w-[45%]">
          {carregando ? (
            <div className="flex h-full w-full items-center justify-center rounded-[13px] bg-white font-sans text-gray-500 shadow-sm">
              Buscando butecos próximos...
            </div>
          ) : (
            <ResultsPanel
              resultados={resultados}
              onVerNoMapa={abrirPaginaDoBar}
            />
          )}
        </div>
      </div>

      <footer className="flex w-full flex-col items-center justify-center gap-2 py-4 text-center font-sans text-sm text-black sm:flex-row sm:gap-4">
        <img
          src="/img-logo.png"
          alt="Comida di Buteco"
          className="h-6 w-auto"
        />

        <span>Comida Di Buteco 2026</span>
        <span className="hidden sm:inline">•</span>
        <span>Explore, descubra e apoie o melhor dos butecos!</span>
      </footer>
    </main>
  );
}

export default App;