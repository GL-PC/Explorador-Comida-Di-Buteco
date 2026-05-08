import type { BarResult } from "../components/ResultsPanel";

const API_BASE_URL = "http://localhost:5000";



export type GeocodeResponse = {
  lat: number;
  lng: number;
};


/*
  Função genérica para chamar a API.
  Ela recebe o endpoint, faz o fetch e:
  - se der certo, retorna o JSON
  - se der erro, lança uma mensagem de erro
*/
async function apiFetch<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`);

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);

    throw new Error(
      errorData?.error || `Erro na requisição: ${response.status}`
    );
  }

  return response.json();
}



/*
  ROTA 1:
  GET /api/geocode?address=<endereco>
  Recebe um endereço em texto e retorna latitude e longitude.
*/
export async function getAddress(
  endereco: string
): Promise<GeocodeResponse> {
  const params = new URLSearchParams({
    address: endereco,
  });

  return apiFetch<GeocodeResponse>(`/api/geocode?${params}`);
}

/*
  ROTA 2A:
  GET /api/butecos/nearby?address=<endereco>&radius_km=<raio>
  Recebe endereço + raio e retorna os bares próximos.
*/
export async function getButecos(
  endereco: string,
  raioKm: number
): Promise<BarResult[]> {
  const params = new URLSearchParams({
    address: endereco,
    radius_km: String(raioKm),
  });

  return apiFetch<BarResult[]>(`/api/butecos/nearby?${params}`);
}

/*
  ROTA 2B:
  GET /api/butecos/nearby?lat=<lat>&lng=<lng>&radius_km=<raio>
  Recebe latitude + longitude + raio e retorna os bares próximos.
*/
export async function getButecosByCords(
  lat: number,
  lng: number,
  raioKm: number
): Promise<BarResult[]> {
  const params = new URLSearchParams({
    lat: String(lat),
    lng: String(lng),
    radius_km: String(raioKm),
  });

  return apiFetch<BarResult[]>(`/api/butecos/nearby?${params}`);
}

/*
  ROTA 3:
  GET /api/butecos
  Recebe todos os butecos do evento
*/


export type ButecoMapaApi = {
  bairro: string;
  cidade: string;
  estado: string;
  imagem_prato: string;
  lat: number | null;
  lng: number | null;
  nome_do_bar: string;
  numero: string;
  rua: string;
};

export async function getAllButecos(): Promise<ButecoMapaApi[]> {
  return apiFetch<ButecoMapaApi[]>("/api/butecos");
}