import { MapPin, Radar, Store } from "lucide-react";

type SearchSummaryProps = {
  enderecoBuscado?: string;
  raioBusca?: number;
};

export default function SearchSummary({
  enderecoBuscado = "Nenhum endereço buscado",
  raioBusca = 5,
}: SearchSummaryProps) {
  function getResultadosEncontrados() {
    return 0;
  }

  const resultadosEncontrados = getResultadosEncontrados();

  return (
    <div className="flex w-full items-center justify-center">
      <div className="flex w-full flex-col items-stretch justify-between gap-4 lg:h-26 lg:flex-row lg:items-center lg:gap-5">
        <div className="flex min-h-20 w-full items-center gap-4 rounded-2xl bg-white px-5 py-4 shadow-sm lg:h-[75%] lg:flex-1 lg:px-6 lg:py-0">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-orange-50 text-orange-500">
            <MapPin size={28} strokeWidth={2.2} />
          </div>

          <div className="flex min-w-0 flex-col font-sans">
            <span className="text-sm text-gray-500">Endereço buscado</span>
            <strong className="truncate text-base text-black">
              {enderecoBuscado || "Nenhum endereço buscado"}
            </strong>
          </div>
        </div>

        <div className="flex min-h-20 w-full items-center gap-4 rounded-2xl bg-white px-5 py-4 shadow-sm lg:h-[75%] lg:w-[22%] lg:px-6 lg:py-0">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-orange-50 text-orange-500">
            <Radar size={28} strokeWidth={2.2} />
          </div>

          <div className="flex min-w-0 flex-col font-sans">
            <span className="text-sm text-gray-500">Raio de busca</span>
            <strong className="text-base text-black">{raioBusca} km</strong>
          </div>
        </div>

        <div className="flex min-h-20 w-full items-center gap-4 rounded-2xl bg-white px-5 py-4 shadow-sm lg:h-[75%] lg:w-[25%] lg:px-6 lg:py-0">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-orange-50 text-orange-500">
            <Store size={28} strokeWidth={2.2} />
          </div>

          <div className="flex min-w-0 flex-col font-sans">
            <span className="text-sm text-gray-500">Bares encontrados</span>
            <strong className="text-base text-black">
              {resultadosEncontrados}
            </strong>
          </div>
        </div>
      </div>
    </div>
  );
}