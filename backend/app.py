"""
Flask application. Entry point do backend.

Execução:
  python -m backend.app
ou:
  flask --app backend.app run --port 5000
"""

import math
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from backend.data_loader import load_data

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

# Carregar dados uma vez ao iniciar
print("[app] Carregando dados...")
store = load_data()
print(f"[app] Servidor pronto com {len(store.bars)} bares")


# ---- Helpers ----------------------------------------------------------------

def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distância great-circle em km entre dois pontos."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def bar_to_dict(bar: dict) -> dict:
    """Serializa um record de bar para JSON."""
    return {
        "cidade": bar["cidade"],
        "nome_do_bar": bar["nome_do_bar"],
        "rua": bar.get("rua", ""),
        "numero": bar.get("numero", ""),
        "bairro": bar.get("bairro", ""),
        "estado": bar.get("estado", ""),
        "imagem_prato": bar["imagem_prato"],
        "lat": bar.get("lat"),
        "lng": bar.get("lng"),
    }


# ---- Routes -----------------------------------------------------------------

@app.get("/api/butecos")
def get_butecos():
    """
    GET /api/butecos
    Params opcionais: ?cidade=Belo+Horizonte
    Retorna todos os bares, ou filtrado por cidade.
    """
    cidade = request.args.get("cidade")
    if cidade:
        results = [b for b in store.bars if b["cidade"] == cidade]
    else:
        results = store.bars

    return jsonify([bar_to_dict(b) for b in results])


@app.get("/api/butecos/nearby")
def get_butecos_nearby():
    """
    GET /api/butecos/nearby?lat=<float>&lng=<float>&radius_km=<float>
    Retorna bares dentro de radius_km da posição (lat, lng).

    Estratégia:
      1. Converte radius_km para graus e usa KDTree.search_radius para pré-filtro
      2. Pós-filtro com haversine para resultado exato
    """
    try:
        lat = float(request.args["lat"])
        lng = float(request.args["lng"])
        radius_km = float(request.args.get("radius_km", 10.0))
    except (KeyError, ValueError):
        abort(400, "Parâmetros obrigatórios: lat, lng. Opcional: radius_km (padrão 10).")

    # Conversão: 1 grau de latitude ≈ 111.2 km
    # Margem de 10% para absorver distorção de longitude
    radius_deg = (radius_km / 111.2) * 1.1

    points = store.tree.search_radius(center=(lat, lng), radius=radius_deg)
    candidates = store.resolve_points(points)

    # Pós-filtro com haversine para resultado preciso
    results = [
        b
        for b in candidates
        if b["lat"] is not None
        and haversine_km(lat, lng, b["lat"], b["lng"]) <= radius_km
    ]

    return jsonify([bar_to_dict(b) for b in results])


@app.get("/api/butecos/bbox")
def get_butecos_bbox():
    """
    GET /api/butecos/bbox?lat_min=<float>&lat_max=<float>&lng_min=<float>&lng_max=<float>
    Retorna bares dentro da bounding box. Mapeia direto para KDTree.search_rect.
    Usado para viewport do mapa (pán/zoom).
    """
    try:
        lat_min = float(request.args["lat_min"])
        lat_max = float(request.args["lat_max"])
        lng_min = float(request.args["lng_min"])
        lng_max = float(request.args["lng_max"])
    except (KeyError, ValueError):
        abort(
            400,
            "Parâmetros obrigatórios: lat_min, lat_max, lng_min, lng_max."
        )

    # KDTree armazena (lat, lng) tuples
    points = store.tree.search_rect(
        point_min=(lat_min, lng_min),
        point_max=(lat_max, lng_max)
    )
    results = store.resolve_points(points)
    return jsonify([bar_to_dict(b) for b in results])


@app.get("/api/cities")
def get_cities():
    """
    GET /api/cities
    Retorna lista ordenada de cidades únicas.
    """
    return jsonify(store.cities)


# ---- Health check -----------------------------------------------------------

@app.get("/")
def health():
    """Health check."""
    return jsonify({"status": "ok", "bars_loaded": len(store.bars)})


# ---- Error handlers ---------------------------------------------------------

@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": str(e.description)}), 400


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


# ---- Entry point ------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
