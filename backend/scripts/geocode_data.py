import csv
import time
from pathlib import Path
from typing import Dict

from geocoder import geocode_batch

SCRIPT_DIR = Path(__file__).parent
BACKEND_DIR = SCRIPT_DIR.parent
DATA_DIR = BACKEND_DIR / "data"
CSV_BRUTO = DATA_DIR / "butecos_comida_di_buteco.csv"
CSV_GEOCODED = DATA_DIR / "butecos_geocoded.csv"


def load_existing_rows() -> Dict[str, dict]:
    if not CSV_GEOCODED.exists():
        return {}
    rows = {}
    with open(CSV_GEOCODED, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            endereco = row.get("endereco", "")
            rows[endereco] = row
    return rows


def save_geocoded(rows: list):
    if not rows:
        return
    fieldnames = ["cidade", "nome_do_bar", "endereco", "imagem_prato", "pagina_url", "lat", "lng"]
    with open(CSV_GEOCODED, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    brutos = []
    with open(CSV_BRUTO, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            brutos.append(row)

    existentes = load_existing_rows()
    pendentes = [b for b in brutos if not existentes.get(b["endereco"], {}).get("lat")]

    print(f"{len(brutos)} linhas no CSV, {len(existentes) - len(pendentes)} já geocodificadas")
    print(f"Geocodificando {len(pendentes)} endereços...")

    start = time.perf_counter()
    batch = geocode_batch([b["endereco"] for b in pendentes], print_progress=True)
    elapsed = time.perf_counter() - start

    geocoded_rows = []
    for bruto in brutos:
        existente = existentes.get(bruto["endereco"])
        if existente and existente.get("lat"):
            geocoded_rows.append(existente)
            continue

        coords = batch.get(bruto["endereco"])
        geocoded_rows.append({
            "cidade": bruto["cidade"],
            "nome_do_bar": bruto["nome_do_bar"],
            "endereco": bruto["endereco"],
            "imagem_prato": bruto.get("imagem_prato", ""),
            "pagina_url": bruto.get("pagina_url", ""),
            "lat": coords[0] if coords else "",
            "lng": coords[1] if coords else "",
        })

    save_geocoded(geocoded_rows)

    novos_ok = sum(1 for c in batch.values() if c)
    novos_fail = len(batch) - novos_ok
    skip = len(brutos) - len(pendentes)
    total_com_coords = sum(1 for r in geocoded_rows if r.get("lat"))

    print(f"\nDONE em {elapsed:.1f}s")
    print(f"  Novos geocodificados: {novos_ok}  Novos falhados: {novos_fail}  Pulados (cache): {skip}")
    print(f"  Total no arquivo: {len(geocoded_rows)} ({total_com_coords} com coordenadas, {len(geocoded_rows) - total_com_coords} sem)")