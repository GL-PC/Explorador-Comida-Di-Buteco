"""
Carrega o CSV geocodificado e constrói a estrutura de dados para o Flask.
Importado pelo app.py na inicialização.
"""

import csv
from pathlib import Path
from backend.src import KDTree


DATA_DIR = Path(__file__).parent / "data"
CSV_GEOCODED = DATA_DIR / "butecos_geocoded.csv"


class DataStore:
    """
    Holds:
      - bars: list[dict]           — todos os 1088 bares (com lat/lng ou None)
      - tree: KDTree               — construída de (lat, lng) tuples (apenas bars com coordenadas)
      - coord_index: dict          — (lat, lng) → list[int] (índices em bars)
      - cities: list[str]          — cidades únicas ordenadas
    """

    def __init__(self, bars: list, tree: KDTree, coord_index: dict, cities: list):
        self.bars = bars
        self.tree = tree
        self.coord_index = coord_index
        self.cities = cities

    def resolve_points(self, points: list) -> list:
        """
        Converte uma lista de (lat, lng) tuples retornada pelo KDTree
        em uma lista de dicts de bares.
        """
        results = []
        seen_indices = set()
        for pt in points:
            key = (float(pt[0]), float(pt[1]))
            for idx in self.coord_index.get(key, []):
                if idx not in seen_indices:
                    seen_indices.add(idx)
                    results.append(self.bars[idx])
        return results


def load_data() -> DataStore:
    """Carrega o CSV geocodificado e constrói a KDTree."""

    if not CSV_GEOCODED.exists():
        raise RuntimeError(
            f"CSV geocodificado não encontrado em {CSV_GEOCODED}. "
            "Execute: python -m backend.scripts.geocode_data"
        )

    # 1. Carregar CSV geocodificado
    bars = []
    with open(CSV_GEOCODED, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=",")
        for row in reader:
            bars.append(dict(row))

    print(f"[data_loader] Carregadas {len(bars)} linhas do CSV geocodificado")

    # 2. Extrair coordenadas, construir KDTree e coord_index
    points = []
    coord_index = {}
    skipped = 0

    for i, bar in enumerate(bars):
        lat_str = bar.get("lat", "").strip()
        lng_str = bar.get("lng", "").strip()

        if not lat_str or not lng_str:
            bar["lat"] = None
            bar["lng"] = None
            skipped += 1
            continue

        try:
            lat = float(lat_str)
            lng = float(lng_str)
            bar["lat"] = lat
            bar["lng"] = lng

            pt = (lat, lng)
            points.append(pt)
            if pt not in coord_index:
                coord_index[pt] = []
            coord_index[pt].append(i)
        except ValueError:
            bar["lat"] = None
            bar["lng"] = None
            skipped += 1

    print(f"[data_loader] {len(points)} bares com coordenadas válidas")
    if skipped:
        print(f"[data_loader] {skipped} bares sem coordenadas (excluídos de buscas espaciais)")

    # 3. Construir KDTree
    tree = KDTree(points) if points else KDTree([])

    # 4. Cidades únicas
    cities = sorted({bar["cidade"] for bar in bars})

    return DataStore(bars=bars, tree=tree, coord_index=coord_index, cities=cities)
