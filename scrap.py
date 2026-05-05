import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time


BASE_URL = "https://comidadibuteco.com.br/butecos/"

CIDADES = {
    "Belo Horizonte": "belo-horizonte",
    "Belém": "belem",
    "Blumenau": "blumenau",
    "Brasília": "brasilia-butecos",
    "Campinas": "campinas",
    "Curitiba": "curitiba-butecos",
    "Florianópolis": "florianopolis",
    "Fortaleza": "fortaleza",
    "Goiás": "goias",
    "Joinville": "joinville",
    "Juiz de Fora": "juiz-de-fora",
    "Londrina": "londrina",
    "Manaus": "manaus-butecos",
    "Maringá": "maringa",
    "Montes Claros": "montes-claros",
    "Poços de Caldas": "pocos-de-caldas",
    "Porto Alegre": "porto-alegre",
    "Recife": "recife",
    "Ribeirão Preto": "ribeirao-preto",
    "Rio de Janeiro - Baixada Fluminense": "nova-iguacu-duque-de-caxias",
    "Rio de Janeiro - Capital": "rio-de-janeiro",
    "Rio de Janeiro - Niterói": "niteroi",
    "Salvador": "salvador",
    "São José do Rio Preto": "sao-jose-do-rio-preto",
    "São Paulo": "sao-paulo",
    "Vale do Aço": "vale-do-aco",
    "Triângulo Mineiro": "triangulo-mineiro",
}


def baixar_html(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    return response.text


def extrair_butecos_da_pagina(html, cidade):
    soup = BeautifulSoup(html, "html.parser")
    dados = []

    cards = soup.select("div.item")

    for card in cards:
        nome_tag = card.select_one(".caption h2")
        endereco_tag = card.select_one(".caption p")
        imagem_tag = card.select_one(".image img")

        nome = nome_tag.get_text(strip=True) if nome_tag else ""
        endereco = endereco_tag.get_text(" ", strip=True) if endereco_tag else ""
        imagem = imagem_tag.get("src", "").strip() if imagem_tag else ""

        if nome:
            dados.append({
                "cidade": cidade,
                "nome_do_bar": nome,
                "endereco": endereco,
                "imagem_prato": imagem
            })

    return dados


def encontrar_proxima_pagina(html):
    soup = BeautifulSoup(html, "html.parser")

    proxima = soup.select_one("a.next.page-link")

    if proxima and proxima.get("href"):
        return proxima["href"]

    return None


def raspar_cidade(cidade, slug):
    resultados = []

    url = urljoin(BASE_URL, slug + "/")

    while url:
        print(f"Raspando {cidade}: {url}")

        try:
            html = baixar_html(url)
        except Exception as e:
            print(f"Erro ao acessar {url}: {e}")
            break

        dados_pagina = extrair_butecos_da_pagina(html, cidade)
        resultados.extend(dados_pagina)

        proxima_url = encontrar_proxima_pagina(html)

        if proxima_url:
            url = proxima_url
        else:
            url = None

        time.sleep(1)

    return resultados


def main():
    todos_os_butecos = []

    for cidade, slug in CIDADES.items():
        dados_cidade = raspar_cidade(cidade, slug)
        todos_os_butecos.extend(dados_cidade)

    df = pd.DataFrame(todos_os_butecos)

    df.to_csv(
        "butecos_comida_di_buteco.csv",
        index=False,
        encoding="utf-8-sig",
        sep=";"
    )

    print("Arquivo CSV gerado com sucesso!")
    print(f"Total de registros: {len(df)}")


if __name__ == "__main__":
    main()