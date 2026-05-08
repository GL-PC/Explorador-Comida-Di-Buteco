import { Search, Eraser, MapPin } from "lucide-react";
import { useState } from "react";

type SearchFormProps = {
  onBuscar: (endereco: string, alcance: number) => void;
  onLimpar: () => void;
};

export default function SearchForm({ onBuscar, onLimpar }: SearchFormProps) {
  const [endereco, setEndereco] = useState("");
  const [alcance, setAlcance] = useState("");
  const [isValidRadious, setIsValidRadious] = useState(true);

  function handleBuscar() {
    const raioNumerico = Number(alcance);

    if (!raioNumerico || raioNumerico <= 0) {
      setIsValidRadious(false);
      return;
    }
    setIsValidRadious(true);
    onBuscar(endereco, raioNumerico);
  }

  function handleLimpar() {
    setEndereco("");
    setAlcance("");
    setIsValidRadious(true);
    onLimpar();
  }

  return (
    <div className="flex w-full items-center justify-center">
      <div className="flex w-full flex-col gap-4 rounded-2xl bg-white px-5 py-5 shadow-sm lg:h-26 lg:flex-row lg:items-center lg:gap-5 lg:px-7 lg:py-0">
        <div className="relative w-full flex-1">
          <MapPin
            size={22}
            className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"
          />

          <input
            type="text"
            value={endereco}
            onChange={(event) => setEndereco(event.target.value)}
            placeholder="Insira seu endereço"
            className="h-14 w-full rounded-xl border border-gray-200 bg-white pl-12 pr-4 font-sans text-base outline-none"
          />
        </div>

        <div className="w-full font-sans lg:w-36 relative ">
          <input
            type="number"
            min={0.01}
            step={0.01}
            value={alcance || ""}
            placeholder="Raio (km)"
            onChange={(event) => setAlcance(event.target.value)}
            className="h-14 w-full rounded-xl border border-gray-200 px-4 text-base outline-none"
          />
          {!isValidRadious && (
            <div className="absolute left-[20px] top-[58px] z-20 whitespace-nowrap rounded-md bg-red-50 px-2 py-1 text-xs font-semibold text-red-500 shadow-sm">
              Valor inválido!
            </div>
          )}
        </div>

        <div className="flex w-full flex-col gap-3 sm:flex-row lg:w-auto">
          <button
            type="button"
            onClick={handleBuscar}
            className="flex h-14 w-full items-center justify-center gap-2 rounded-xl bg-orange-400 px-8 font-sans font-semibold text-white transition hover:cursor-pointer hover:bg-orange-500 lg:w-auto"
          >
            <Search size={20} />
            Buscar
          </button>

          <button
            type="button"
            onClick={handleLimpar}
            className="flex h-14 w-full items-center justify-center gap-2 rounded-xl border border-orange-400 bg-white px-8 font-sans font-semibold text-orange-500 transition hover:cursor-pointer hover:bg-orange-400 hover:text-white lg:w-auto"
          >
            <Eraser size={20} />
            Limpar
          </button>
        </div>
      </div>
    </div>
  );
}