import re
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

MAX_SIM_REQ = 5

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

PATTERNS = [
    (r'"latitude"\s*:\s*(-?\d+\.\d+)', r'"longitude"\s*:\s*(-?\d+\.\d+)'),
    (r'itemprop="latitude"\s+content="(-?\d+\.\d+)"', r'itemprop="longitude"\s+content="(-?\d+\.\d+)"'),
    (r'\[(-?\d{1,3}\.\d{6,}),(-?\d{1,3}\.\d{6,})\]', None),
    (r'@(-?\d+\.\d+),(-?\d+\.\d+)', None),
]


def _parse_json_response(text: str) -> tuple[float, float] | None:
    """Resposta no formato JSON )]}'  — coords em [escala, lng, lat]."""
    m = re.search(r'\[(\d{4,}[\d.]*),(-?\d+\.\d+),(-?\d+\.\d+)\]', text)
    if m:
        return float(m.group(3)), float(m.group(2))  # (lat, lng)
    return None


def _fetch_coords(query: str) -> tuple[float, float] | None:
    params = {"tbm": "map", "hl": "pt-BR", "gl": "br", "q": query}
    url = "https://www.google.com/search?" + urlencode(params)
    try:
        r = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=10)
    except requests.RequestException:
        return None

    text = r.text

    if text.startswith(")]}'"):
        return _parse_json_response(text)

    for lat_pat, lng_pat in PATTERNS:
        if lng_pat is None:
            m = re.search(lat_pat, text)
            if m:
                return float(m.group(1)), float(m.group(2))
        else:
            m_lat = re.search(lat_pat, text)
            m_lng = re.search(lng_pat, text)
            if m_lat and m_lng:
                return float(m_lat.group(1)), float(m_lng.group(1))

    return None


def _normalize(address: str) -> str:
    """Substitui | por vírgula e remove notas após –."""
    addr = re.sub(r'\s*\|\s*', ', ', address)
    addr = re.sub(r'\s*–\s*[^,]+', '', addr)
    addr = re.sub(r'\s{2,}', ' ', addr)
    return addr.strip().strip(',')


def _extract_location(address: str) -> str | None:
    """Extrai 'Cidade - UF' ou 'Cidade, UF' do final do endereço."""
    m = re.search(r'([A-Za-zÀ-ú\s]+)\s*[-,]\s*([A-Z]{2})\s*$', address)
    if m:
        return f"{m.group(1).strip()} - {m.group(2)}"
    return None


def _simplify(address: str) -> str | None:
    """Extrai só rua + cidade a partir do formato 'Rua X | Bairro, Cidade - UF'."""
    # captura tudo antes do primeiro | ou vírgula, + localização no final
    m = re.search(r'^(.+?)\s*[|,]', address)
    loc = _extract_location(address)
    if m and loc:
        street = m.group(1).strip()
        simplified = f"{street}, {loc}"
        if simplified != _normalize(address):
            return simplified
    return None


def geocode(address: str) -> tuple[float, float] | None:
    # 1ª: endereço normalizado
    result = _fetch_coords(_normalize(address))
    if result:
        return result

    # 2ª: só rua + cidade - UF
    simple = _simplify(address)
    if simple:
        result = _fetch_coords(simple)
        if result:
            return result

    return None


def geocode_batch(addresses: list[str], print_progress: bool = False) -> dict[str, tuple[float, float] | None]:
    results: dict[str, tuple[float, float] | None] = {}
    with ThreadPoolExecutor(max_workers=MAX_SIM_REQ) as executor:
        future_to_addr = {executor.submit(geocode, addr): addr for addr in addresses}
        for i, future in enumerate(as_completed(future_to_addr)):
            results[future_to_addr[future]] = future.result()
            if print_progress:
                print(f"[{i+1}/{len(addresses)}] Geocoded: {future_to_addr[future]} -> {results[future_to_addr[future]]}")
    return results
