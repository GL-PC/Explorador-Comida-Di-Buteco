import MapView from "./components/MapView";
import pin from "./assets/pin.png";
import home from "./assets/search-pin.png";
import mapIcon from "./assets/mapIcon.png";
import SearchForm from "./components/SearchForm";
import SearchSummary from "./components/SearchSummary";
import { useState } from "react";
import ResultsPanel, { type BarResult } from "./components/ResultsPanel";

// exemplo mockado
const resultadosMockados: BarResult[] = [
  {
    id: 1,
    nome: "222",
    endereco: "R. Francisco Deslandes, 222 - Belo Horizonte - MG",
    bairro: "",
    distanciaKm: 0.61,
    imagemPratoUrl:
      "https://cdb-static-files.s3.amazonaws.com/wp-content/uploads/2026/03/09110856/222_buraquimquente_bh_2026_pauloti_unibh-4859.jpg",
    paginaUrl: "https://comidadibuteco.com.br/buteco/3100-revision-v1/",
  },
  {
    id: 2,
    nome: "Alexandre’s Bar",
    endereco: "R. David Alves do Vale, 68 - Santa Rosa, Belo Horizonte - MG",
    bairro: "Santa Rosa",
    distanciaKm: 0.84,
    imagemPratoUrl:
      "https://cdb-static-files.s3.amazonaws.com/wp-content/uploads/2026/03/09110859/alexandresbar_porcoamostarda_pauloti_unibh-3271.jpg",
    paginaUrl: "https://comidadibuteco.com.br/buteco/alexandres-bar/",
  },
  {
    id: 3,
    nome: "Bar da Gisa",
    endereco: "Rua Maria Ferreira da Silva, 367 - Belo Horizonte - MG",
    bairro: "",
    distanciaKm: 1.05,
    imagemPratoUrl:
      "https://cdb-static-files.s3.amazonaws.com/wp-content/uploads/2026/03/09111119/bardagisa_ajoelhoutemquerezar_giovanaevilyn_unibh-3157.jpg",
    paginaUrl: "https://comidadibuteco.com.br/buteco/bar-da-gisa/",
  },
];

function App() {
  const [enderecoBuscado, setEnderecoBuscado] = useState("");
  const [raioBusca, setRaioBusca] = useState(0);
  const [resultados, setResultados] = useState<BarResult[]>([]);

  function receberBusca(endereco: string, alcance: number) {
    setEnderecoBuscado(endereco);
    setRaioBusca(alcance);
    setResultados(resultadosMockados);
  }

  function limparBusca() {
    setEnderecoBuscado("");
    setRaioBusca(0);
    setResultados([]);
  }

  function abrirPaginaDoBar(bar: BarResult) {
    window.open(bar.paginaUrl, "_blank", "noopener,noreferrer");
  }

  return (
    <main className="min-h-screen px-4 py-6 sm:px-6">
      <header className="mb-5 flex w-full flex-col items-center justify-center gap-3">
        <h1 className="text-center text-4xl font-bold text-[#144a11] sm:text-5xl">
          Explorador Comida di Buteco 2026
        </h1>

        <h2 className="text-center text-base font-normal text-black sm:text-lg">
          Encontre os bares participantes do Comida di Buteco 2026!
        </h2>
      </header>

      <div className="mx-auto mb-4 flex w-full items-center justify-center lg:w-[80%]">
        <SearchForm onBuscar={receberBusca} onLimpar={limparBusca} />
      </div>

      <div className="mx-auto mb-5 flex w-full items-center justify-center lg:w-[80%]">
        <SearchSummary
          enderecoBuscado={enderecoBuscado}
          raioBusca={raioBusca}
        />
      </div>

      <div className="mx-auto mb-4 flex w-full flex-col gap-4 lg:h-[50vh] lg:w-[85%] lg:flex-row">
        <div className="flex h-107.5 w-full flex-col rounded-[13px] bg-white p-4 lg:h-full lg:w-[55%]">
          <div className="flex flex-col gap-3 pb-3 font-sans sm:flex-row sm:items-center sm:justify-between">
            <div className="flex">
              <div className="flex items-center justify-center gap-2 px-3">
                <img src={mapIcon} alt="Mapa" className="h-4 w-auto" />
                <p className="font-bold">Mapa de Busca</p>
              </div>
            </div>

            <div className="flex flex-col gap-2 text-gray-500 sm:flex-row sm:gap-5">
              <div className="flex items-center gap-1 px-3">
                <img src={pin} alt="Bares participantes" className="h-5 w-auto" />
                <p>Bares Participantes</p>
              </div>

              <div className="flex items-center gap-1 px-3">
                <img src={home} alt="Endereço buscado" className="h-6 w-auto" />
                <p>Endereço Buscado</p>
              </div>
            </div>
          </div>

          <div className="min-h-0 flex-1">
            <MapView />
          </div>
        </div>

        <div className="h-130 w-full rounded-[13px] lg:h-full lg:w-[45%]">
          <ResultsPanel
            resultados={resultados}
            onVerNoMapa={abrirPaginaDoBar}
          />
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