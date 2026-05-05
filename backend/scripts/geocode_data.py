"""
One-time geocoding script. Lê CSV bruto, extrai coordenadas do Google Maps URL,
e grava CSV enriquecido com lat/lng.

Execução: python -m backend.scripts.geocode_data

Pesquisa cada endereço no Google Maps (via Playwright com Firefox),
extrai as coordenadas da URL do resultado.
"""

import csv
import re
import asyncio
import urllib.parse
from pathlib import Path
from typing import Dict, Tuple, Optional

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Instale playwright: pip install playwright")
    print("Depois instale firefox: python -m playwright install firefox")
    exit(1)

SCRIPT_DIR = Path(__file__).parent
BACKEND_DIR = SCRIPT_DIR.parent
DATA_DIR = BACKEND_DIR / "data"
CSV_BRUTO = DATA_DIR / "butecos_comida_di_buteco.csv"
CSV_GEOCODED = DATA_DIR / "butecos_geocoded.csv"

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


def parse_endereco(endereco: str) -> Dict[str, str]:
    """
    Parseia formato: "rua, numero | bairro, cidade - estado"
    Retorna: {"rua": "", "numero": "", "bairro": "", "cidade": "", "estado": ""}
    """
    result = {"rua": "", "numero": "", "bairro": "", "cidade": "", "estado": ""}

    parts = endereco.split("|")
    if len(parts) != 2:
        return result

    esquerda = parts[0].strip()
    direita = parts[1].strip()

    if "," in esquerda:
        esquerda_parts = esquerda.rsplit(",", 1)
        result["rua"] = esquerda_parts[0].strip()
        result["numero"] = esquerda_parts[1].strip()
    else:
        result["rua"] = esquerda

    if "-" in direita:
        direita_parts = direita.rsplit("-", 1)
        bairro_cidade = direita_parts[0].strip()
        result["estado"] = direita_parts[1].strip()

        if "," in bairro_cidade:
            bairro_cidade_parts = bairro_cidade.rsplit(",", 1)
            result["bairro"] = bairro_cidade_parts[0].strip()
            result["cidade"] = bairro_cidade_parts[1].strip()
        else:
            result["cidade"] = bairro_cidade
    else:
        result["cidade"] = direita

    return result


def load_existing_rows() -> Dict[str, dict]:
    """Se butecos_geocoded.csv já existe, carrega as linhas já geocodificadas."""
    if not CSV_GEOCODED.exists():
        return {}

    rows = {}
    with open(CSV_GEOCODED, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            endereco = row.get("endereco", "")
            rows[endereco] = row
    return rows


def extract_coords_from_maps_url(html: str) -> Optional[Tuple[float, float]]:
    """
    Extrai coordenadas (lat, lng) da URL do Google Maps na página de resultado.
    Procura por padrão: @-25.4528096,-49.2126964 ou !3d-25.4528145!4d-49.2101215
    """
    # Padrão 1: @lat,lng (mais recente)
    match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', html)
    if match:
        try:
            return (float(match.group(1)), float(match.group(2)))
        except ValueError:
            pass

    # Padrão 2: !3d<lat>!4d<lng> (formato antigo)
    match = re.search(r'!3d(-?\d+\.\d+).*?!4d(-?\d+\.\d+)', html)
    if match:
        try:
            return (float(match.group(1)), float(match.group(2)))
        except ValueError:
            pass

    return None


async def geocode_address(endereco_full: str, browser) -> Optional[Tuple[float, float]]:
    """
    Pesquisa um endereco no Google Maps (via Playwright) e extrai as coordenadas.
    Aguarda até que as coordenadas apareçam na URL (tentativas com delay).
    """
    query = endereco_full.replace("|", ",").strip()
    url = f"https://www.google.com/maps/search/{urllib.parse.quote(query)}"

    try:
        context = await browser.new_context(viewport={"width": 1280, "height": 720}, locale="pt-BR")
        page = await context.new_page()
        await page.goto(url, wait_until="load", timeout=30000)

        # Aguardar carregamento de rede
        await page.wait_for_load_state("networkidle", timeout=15000)

        # Tentar extrair coordenadas da URL com múltiplas tentativas
        # (às vezes leva um tempo extra para renderizar)
        coords = None
        for tentativa in range(5):
            final_url = page.url
            coords = extract_coords_from_url(final_url)
            if coords:
                break
            # Aguardar e tentar novamente
            await asyncio.sleep(2.0)

        await context.close()
        return coords
    except Exception as e:
        return None


async def geocode_all():
    """Executa o fluxo completo de geocodificacao."""

    # Carregar CSV bruto
    brutos = []
    with open(CSV_BRUTO, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            brutos.append(row)

    print(f"Carregadas {len(brutos)} linhas do CSV bruto")

    # Carregar linhas ja geocodificadas (se existirem)
    existentes = load_existing_rows()
    print(f"Encontradas {len(existentes)} linhas ja geocodificadas")

    # Preparar output
    geocoded_rows = []
    geocoded_count = 0
    skipped_count = 0
    failed_count = 0

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)

        for i, bruto in enumerate(brutos):
            endereco_bruto = bruto["endereco"]
            cidade = bruto["cidade"]
            nome = bruto["nome_do_bar"]

            # Verificar se ja foi geocodificado
            if endereco_bruto in existentes:
                geocoded_rows.append(existentes[endereco_bruto])
                skipped_count += 1
                print(f"[{i+1:4d}/{len(brutos)}] SKIP (cached): {nome[:40]}")
                continue

            # Parsear endereco
            parsed = parse_endereco(endereco_bruto)

            lat, lng = None, None
            coords = await geocode_address(endereco_bruto, browser)
            if coords:
                lat, lng = coords
                geocoded_count += 1
                print(f"[{i+1:4d}/{len(brutos)}] OK: {nome[:40]} -> ({lat:.4f}, {lng:.4f})")
            else:
                print(f"[{i+1:4d}/{len(brutos)}] FAIL: {nome[:40]}")
                failed_count += 1

            # Montar linha geocodificada
            row = {
                "cidade": bruto["cidade"],
                "nome_do_bar": bruto["nome_do_bar"],
                "rua": parsed["rua"],
                "numero": parsed["numero"],
                "bairro": parsed["bairro"],
                "estado": parsed["estado"],
                "imagem_prato": bruto["imagem_prato"],
                "lat": lat if lat is not None else "",
                "lng": lng if lng is not None else "",
            }
            geocoded_rows.append(row)

            # Salvar a cada 10
            if (i + 1) % 10 == 0:
                save_geocoded(geocoded_rows)
                print(f"  -> salvou {len(geocoded_rows)} linhas ate agora")

        await browser.close()

    # Salvar final
    save_geocoded(geocoded_rows)
    print(f"\n{'='*60}")
    print(f"DONE!")
    print(f"  Geocodificados (novos): {geocoded_count}")
    print(f"  Pulados (cache): {skipped_count}")
    print(f"  Falhados: {failed_count}")
    print(f"  Total no arquivo: {len(geocoded_rows)}")
    print(f"  Arquivo: {CSV_GEOCODED}")


def save_geocoded(rows: list):
    """Grava CSV geocodificado com delimitador padrão (,)."""
    if not rows:
        return

    fieldnames = ["cidade", "nome_do_bar", "rua", "numero", "bairro", "estado", "imagem_prato", "lat", "lng"]
    with open(CSV_GEOCODED, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    asyncio.run(geocode_all())
