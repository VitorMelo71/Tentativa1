import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
import time

# Configuração da API do Firestore e do Google Maps
FIRESTORE_API_KEY = "AIzaSyCrTdYbECD-ECWNirQBBfPjggedBrRYMeg"
PROJECT_ID = "banco-gps"
COLLECTION = "CoordenadasGPS"

FIRESTORE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/{COLLECTION}?key={FIRESTORE_API_KEY}"

# Função para buscar dados do Firestore via API REST
def get_tracking_data():
    response = requests.get(FIRESTORE_URL)
    data = response.json()

    records = []
    if 'documents' in data:
        for doc in data['documents']:
            fields = doc['fields']
            records.append({
                'latitude': float(fields['latitude']['stringValue']),
                'longitude': float(fields['longitude']['stringValue']),
                'status': fields['status']['stringValue']
            })
    return pd.DataFrame(records)

# Configuração da página para celular (iPhone 11)
st.set_page_config(page_title="CEAMAZON GPS", layout="centered")

st.title("CEAMAZON GPS - Rastreamento")

# Inicializa o estado do mapa com uma visualização padrão
if 'map_initialized' not in st.session_state:
    st.session_state['zoom'] = 15
    st.session_state['center'] = [-1.46906, -48.44755]  # Coordenadas padrão
    st.session_state['map_initialized'] = True

# Cria um espaço reservado para o mapa
map_placeholder = st.empty()

# Inicializa a visualização inicial do mapa usando Pydeck
view_state = pdk.ViewState(
    latitude=st.session_state['center'][0],
    longitude=st.session_state['center'][1],
    zoom=st.session_state['zoom'],
    pitch=0,
)

# Exibe o mapa inicialmente
initial_layer = pdk.Layer(
    "ScatterplotLayer",
    data=pd.DataFrame([]),  # Inicialmente vazio
    get_position='[longitude, latitude]',
    get_color='[200, 30, 0, 160]',
    get_radius=200,
)

deck = pdk.Deck(
    layers=[initial_layer],
    initial_view_state=view_state,
    map_style="mapbox://styles/mapbox/streets-v11"
)

# Renderiza o mapa
map_placeholder.pydeck_chart(deck)

# Atualiza apenas os pontos de localização sem recarregar o mapa inteiro
while True:
    # Carregar dados do Firestore
    data_df = get_tracking_data()

    if not data_df.empty:
        # Criar a camada de pontos atualizada
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=data_df,
            get_position='[longitude, latitude]',
            get_color='[200, 30, 0, 160]',
            get_radius=200,
        )

        # Atualizar o mapa com a nova camada, mantendo a visualização
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_style="mapbox://styles/mapbox/streets-v11"
        )

        # Renderizar o mapa atualizado
        map_placeholder.pydeck_chart(deck)

    # Pausar por um intervalo de tempo antes da próxima atualização
    time.sleep(10)
