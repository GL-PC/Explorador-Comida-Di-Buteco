import { ListOrdered, ChevronRight,ClipboardList } from "lucide-react";

export type BarResult = {
  id: number;
  nome: string;
  endereco: string;
  bairro: string;
  distanciaKm: number;
  imagemPratoUrl: string;
  paginaUrl: string;
  lat?: number;
  lng?: number;
};

type ResultsPanelProps = {
  resultados: BarResult[];
  onVerNoMapa?: (bar: BarResult) => void;
};

export default function ResultsPanel({
  resultados,
  onVerNoMapa,
}: ResultsPanelProps) {
  return (
    <div className="flex h-full w-full flex-col overflow-hidden rounded-[13px] bg-white font-sans shadow-sm">
      <div className="flex items-center justify-between border-b border-[#eee1d0] px-5 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-orange-50 text-orange-500">
            <ClipboardList size={20} strokeWidth={2.3} />
          </div>

          <h3 className="text-[18px] font-bold text-slate-900">Resultados</h3>
        </div>
      </div>

      <div className="hidden grid-cols-[120px_1fr_110px_44px] items-center border-b border-[#eee1d0] bg-[#faf7f2] px-4 py-3 text-sm font-semibold text-slate-700 sm:grid">
        <div className="text-center">Prato</div>
        <div className="text-center">Bar</div>
        <div className="text-center">Distância</div>
        <div></div>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto">
        {resultados.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-3 px-8 text-center font-sans">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-orange-50 text-orange-500">
              <ListOrdered size={28} strokeWidth={2.2} />
            </div>

            <div>
              <p className="text-base font-bold text-slate-800">
                Nenhum resultado ainda
              </p>

              <p className="mt-1 max-w-[280px] text-sm leading-relaxed text-gray-500">
                Digite um endereço e um raio para encontrar os butecos próximos.
              </p>
            </div>
          </div>
        ) : (
          resultados.map((bar) => (
            <div
              key={bar.id}
              onClick={() => onVerNoMapa?.(bar)}
              className="cursor-pointer border-b border-[#f2e6d8] px-4 py-4 transition hover:bg-orange-50/60 sm:grid sm:grid-cols-[120px_1fr_110px_44px] sm:items-center"
            >
              <div className="mb-3 flex justify-center sm:mb-0">
                <img
                  src={bar.imagemPratoUrl}
                  alt={`Prato do ${bar.nome}`}
                  className="h-32 w-full rounded-md object-cover sm:h-20 sm:w-24"
                />
              </div>

              <div className="flex flex-col items-center justify-center px-2 text-center">
                <p className="text-[15px] font-bold leading-tight text-slate-900">
                  {bar.nome}
                </p>

                <p className="mt-1 text-[13px] leading-tight text-gray-600">
                  {bar.endereco}
                </p>

                {bar.bairro && (
                  <p className="mt-1 text-[13px] text-gray-500">{bar.bairro}</p>
                )}
              </div>

              <div className="mt-3 text-center text-[15px] font-bold text-orange-600 sm:mt-0">
                {bar.distanciaKm.toFixed(2)} km
              </div>

              <div className="mt-3 flex justify-center sm:mt-0">
                <button
                  type="button"
                  onClick={(event) => {
                    event.stopPropagation();
                    onVerNoMapa?.(bar);
                  }}
                  className="flex h-8 w-8 cursor-pointer items-center justify-center rounded-full text-slate-500 transition hover:bg-orange-100 hover:text-orange-500"
                  title="Ver mais detalhes"
                >
                  <ChevronRight size={20} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}