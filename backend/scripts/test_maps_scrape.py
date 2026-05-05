"""
Script de teste: valida se consegue extrair coordenadas de URLs do Google Maps.
Usa Playwright com Firefox para renderizar JavaScript.
Testa com alguns enderecos antes de rodar o geocode_data.py completo.
"""

import re
import urllib.parse
import asyncio
from typing import Optional, Tuple
from playwright.async_api import async_playwright

ENDERECОS_TESTE = [
    "Rua Roraima, 1369 | Cajuru, Curitiba - PR",
    "R. Francisco Deslandes, 222 | Belo Horizonte - MG",
    "Rua da Sinfonia, 253 | Santa Amelia, Belo Horizonte - MG",
]


def extract_coords_from_url(url: str) -> Optional[Tuple[float, float]]:
    """Extrai coordenadas (lat, lng) de uma URL do Google Maps."""
    # Padrao: @lat,lng (mais recente)
    match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
    if match:
        try:
            return (float(match.group(1)), float(match.group(2)))
        except ValueError:
            pass

    # Padrao: !3d<lat>!4d<lng> (formato antigo)
    match = re.search(r'!3d(-?\d+\.\d+).*?!4d(-?\d+\.\d+)', url)
    if match:
        try:
            return (float(match.group(1)), float(match.group(2)))
        except ValueError:
            pass

    return None


async def test_geocode(endereco_full: str, browser):
    """Testa geocodificacao de um endereco usando Playwright."""
    print(f"\n{'='*70}")
    print(f"Testando: {endereco_full}")
    print(f"{'='*70}")

    query = endereco_full.replace("|", ",").strip()
    url = f"https://www.google.com/maps/search/{urllib.parse.quote(query)}"
    print(f"URL: {url}\n")

    page = None
    try:
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            locale="pt-BR"
        )
        page = await context.new_page()
        await page.goto(url, wait_until="load", timeout=30000)

        # Aguardar carregamento de rede
        print("Aguardando carregamento de rede...")
        await page.wait_for_load_state("networkidle", timeout=15000)

        # Tentar extrair coordenadas com multiplas tentativas
        print("Tentando extrair coordenadas...")
        coords = None
        for tentativa in range(5):
            final_url = page.url
            print(f"  Tentativa {tentativa + 1}/5: {final_url[:80]}...")

            coords = extract_coords_from_url(final_url)
            if coords:
                lat, lng = coords
                print(f"\n[OK] Coordenadas extraidas: ({lat:.6f}, {lng:.6f})")
                await context.close()
                return coords

            if tentativa < 4:
                print(f"  Aguardando 2s antes da proxima tentativa...")
                await asyncio.sleep(2.0)

        print(f"\n[FAIL] Nao conseguiu extrair coordenadas apos 5 tentativas")
        await context.close()
        return None

    except Exception as e:
        print(f"[ERROR] {e}")
        if page:
            try:
                await page.close()
            except:
                pass
        return None


async def main():
    """Roda os testes."""
    print("TESTE: Extracao de coordenadas do Google Maps com Playwright")
    print("=" * 70)

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)

        resultados = {}
        for endereco in ENDERECОS_TESTE:
            coords = await test_geocode(endereco, browser)
            resultados[endereco] = coords

        await browser.close()

    print(f"\n\n{'='*70}")
    print("RESUMO")
    print(f"{'='*70}")
    for endereco, coords in resultados.items():
        if coords:
            print(f"[OK] {endereco} -> {coords}")
        else:
            print(f"[FAIL] {endereco} -> FALHOU")


if __name__ == "__main__":
    asyncio.run(main())
