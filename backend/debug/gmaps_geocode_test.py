import re
import time
import requests
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor, as_completed

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
MAX_SIM_REQ = 5  # requisições simultâneas

PATTERNS = [
    (r'"latitude"\s*:\s*(-?\d+\.\d+)', r'"longitude"\s*:\s*(-?\d+\.\d+)'),
    (r'itemprop="latitude"\s+content="(-?\d+\.\d+)"', r'itemprop="longitude"\s+content="(-?\d+\.\d+)"'),
    (r'\[(-?\d{1,3}\.\d{6,}),(-?\d{1,3}\.\d{6,})\]', None),
    (r'@(-?\d+\.\d+),(-?\d+\.\d+)', None),
]


def geocode(address: str) -> tuple[str, tuple[float, float] | None]:
    params = {"tbm": "map", "hl": "pt-BR", "gl": "br", "q": address}
    url = "https://www.google.com/search?" + urlencode(params)
    try:
        r = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=10)
    except requests.RequestException:
        return address, None

    for lat_pat, lng_pat in PATTERNS:
        if lng_pat is None:
            m = re.search(lat_pat, r.text)
            if m:
                return address, (float(m.group(1)), float(m.group(2)))
        else:
            m_lat = re.search(lat_pat, r.text)
            m_lng = re.search(lng_pat, r.text)
            if m_lat and m_lng:
                return address, (float(m_lat.group(1)), float(m_lng.group(1)))

    return address, None


def geocode_batch(addresses: list[str]) -> dict[str, tuple[float, float] | None]:
    results = {}
    with ThreadPoolExecutor(max_workers=MAX_SIM_REQ) as executor:
        futures = {executor.submit(geocode, addr): addr for addr in addresses}
        for future in as_completed(futures):
            address, coords = future.result()
            results[address] = coords
    return results


def dump_html(address: str):
    """Faz a requisição e imprime o HTML cru para depuração."""
    from urllib.parse import urlencode
    params = {"tbm": "map", "hl": "pt-BR", "gl": "br", "q": address}
    url = "https://www.google.com/search?" + urlencode(params)
    r = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=10)
    print(f"\n=== HTML dump: {address} ===")
    print(f"status={r.status_code}  len={len(r.text)}")
    print(r.text[:3000])


if __name__ == "__main__":
    TEST_ADDRESSES = [
        # falhas Brasília — dump HTML para análise
        "SCLRN 706, Brasília - DF",          # versão já simplificada
        "QD C 01, Taguatinga - DF",           # versão já simplificada
        "Quadra CCSW, 5, Brasília - DF",
        "Rua 7, 330, Vicente Pires, Brasília - DF",
    ]

    print("--- Tentando geocode ---")
    for addr in TEST_ADDRESSES:
        result = geocode(addr)
        print(f"{addr} -> {result}")

    print("\n--- HTML dump do primeiro que falhou ---")
    dump_html("SCLRN 706, Brasília - DF")
    
    start = time.perf_counter()
    results = geocode_batch(TEST_ADDRESSES)
    elapsed = time.perf_counter() - start

    for address in TEST_ADDRESSES:
        coords = results[address]
        if coords:
            lat, lng = coords
            print(f"{address}")
            print(f"  lat={lat:.7f}, lng={lng:.7f}")
        else:
            print(f"{address}")
            print(f"  Não geocodificado.")

    print(f"\n{len(TEST_ADDRESSES)} endereços em {elapsed:.2f}s")