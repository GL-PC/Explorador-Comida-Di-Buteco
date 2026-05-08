# Explorador Comida di Buteco

Aplicação web para descobrir os bares participantes do **Comida di Buteco 2026** próximos ao usuário. Pesquisa por endereço, com um raio de busca, e visualize os estabelecimentos próximos no mapa.

## Funcionalidades

- Busca por endereço com geocodificação via Google Maps
- Filtro por raio de distância (km), e pela área visível do mapa (bounding box)
- Seleção dos bares filtrados por uma KDTree para buscas por coordenadas eficientes
- Mapa interativo com marcadores dos bares
- Listagem dos resultados ordenados por distância, com foto do prato, endereço e link para a página do bar
- Índice espacial KDTree para buscas de proximidade eficientes (~1.086 bares geocodificados)

## Stack

**Frontend** — React 19 + TypeScript + Vite + Tailwind CSS + Leaflet

**Backend** — Python + Flask + KDTree

## Rodando o projeto

### Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

O backend sobe em `http://localhost:5000` e o frontend em `http://localhost:5173`.
