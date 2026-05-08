import math

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


def bar_to_frontend_dict(bar: dict, bar_id: int, distancia_km: float) -> dict:
    """Serializa um bar no formato esperado pelo frontend."""
    partes_rua = ", ".join(filter(None, [bar.get("rua", ""), bar.get("numero", "")]))
    partes_cidade = " - ".join(filter(None, [bar.get("cidade", ""), bar.get("estado", "")]))
    endereco = " - ".join(filter(None, [partes_rua, partes_cidade]))
    return {
        "id": bar_id,
        "nome": bar.get("nome_do_bar", ""),
        "endereco": endereco,
        "distanciaKm": round(distancia_km, 2),
        "imagemPratoUrl": bar.get("imagem_prato", ""),
        "paginaUrl": bar.get("pagina_url", ""),
        "lat": bar.get("lat"),
        "lng": bar.get("lng"),
    }