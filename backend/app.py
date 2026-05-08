from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from data_loader import load_data
from scripts.geocoder import geocode
from scripts.utils import haversine_km, bar_to_dict, bar_to_frontend_dict

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

# Carregar dados uma vez ao iniciar
print("[app] Carregando dados...")
store = load_data()
print(f"[app] Servidor pronto com {len(store.bars)} bares")


# ____________ ENDPOINTS ____________________________

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


@app.get("/api/geocode")
def get_geocode():
    """
    GET /api/geocode?address=<str>
    Geocodifica um endereço usando Google Maps e retorna {lat, lng}.
    """
    address = request.args.get("address", "").strip()
    if not address:
        abort(400, "Parâmetro obrigatório: address")
    coords = geocode(address)
    if not coords:
        abort(404, "Endereço não encontrado")
    return jsonify({"lat": coords[0], "lng": coords[1]})


@app.get("/api/butecos/nearby")
def get_butecos_nearby():
    """
    GET /api/butecos/nearby?address=<str>&radius_km=<float>
    GET /api/butecos/nearby?lat=<float>&lng=<float>&radius_km=<float>
    Retorna bares dentro de radius_km, ordenados por distância.
    Aceita endereço textual (geocodificado via Google Maps) ou coordenadas diretas.
    """
    try:
        address = request.args.get("address", "").strip()
        if address:
            coords = geocode(address)
            if not coords:
                abort(404, "Endereço não encontrado")
            lat, lng = coords
        else:
            lat = float(request.args["lat"])
            lng = float(request.args["lng"])
        radius_km = float(request.args.get("radius_km", 10.0))
    except (KeyError, ValueError):
        abort(400, "Forneça address ou lat+lng. Opcional: radius_km (padrão 10).")

    radius_deg = (radius_km / 111.2) * 1.1
    points = store.tree.search_radius(center=(lat, lng), radius=radius_deg)
    candidates = store.resolve_points(points)

    results = []
    for i, b in enumerate(candidates):
        if b["lat"] is None:
            continue
        dist = haversine_km(lat, lng, b["lat"], b["lng"])
        if dist <= radius_km:
            results.append(bar_to_frontend_dict(b, i + 1, dist))

    results.sort(key=lambda x: x["distanciaKm"])
    return jsonify(results)


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

# ________ ERROR HANDLERS ______________________

@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": str(e.description)}), 400


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


# _____________ MAIN ____________________________

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
