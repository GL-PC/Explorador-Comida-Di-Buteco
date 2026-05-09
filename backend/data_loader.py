import csv
from pathlib import Path
from src import KDTree


DATA_DIR = Path(__file__).parent / "data"
CSV_GEOCODED = DATA_DIR / "butecos_geocoded.csv"


def _parse_endereco(endereco: str, cidade: str) -> tuple:
    """Splits 'Rua X, N | Bairro, Cidade - Estado' into (rua, numero, bairro, estado)."""
    rua = numero = bairro = estado = ""
    if "|" not in endereco:
        return rua, numero, bairro, estado

    street_part, loc_part = endereco.split("|", 1)
    street_part = street_part.strip()
    loc_part = loc_part.strip()

    if " - " in loc_part:
        loc_no_estado, estado = loc_part.rsplit(" - ", 1)
        estado = estado.strip()
        loc_no_estado = loc_no_estado.strip()
        if cidade and loc_no_estado.endswith(cidade):
            bairro = loc_no_estado[: -len(cidade)].strip().rstrip(",").strip()
        else:
            parts = [s.strip() for s in loc_no_estado.split(",")]
            if len(parts) > 1:
                bairro = parts[0]

    parts = [s.strip() for s in street_part.rsplit(",", 1)]
    if len(parts) == 2:
        rua, numero = parts[0], parts[1]
    else:
        rua = street_part

    return rua, numero, bairro, estado


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
            bar = dict(row)
            rua, numero, bairro, estado = _parse_endereco(
                bar.get("endereco", ""), bar.get("cidade", "")
            )
            bar["rua"] = rua
            bar["numero"] = numero
            bar["bairro"] = bairro
            bar["estado"] = estado
            bars.append(bar)

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
