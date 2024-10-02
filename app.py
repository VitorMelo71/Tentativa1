import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import time

# Configuração da API do Firestore e do Google Maps
FIRESTORE_API_KEY = "AIzaSyCrTdYbECD-ECWNirQBBfPjggedBrRYMeg"
GOOGLE_MAPS_API_KEY = "AIzaSyAvBYntkiyjBNpU96UdMSoD5cavd3lqQtY"
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

# Inicializa o mapa apenas uma vez e mantém a posição e o zoom
if 'map_initialized' not in st.session_state:
    st.session_state['zoom'] = 15
    st.session_state['center'] = [-1.46906, -48.44755]  # Coordenadas padrão
    st.session_state['map_initialized'] = True

# Cria um espaço reservado para o mapa
map_placeholder = st.empty()

# Inicializa o mapa usando Google Maps
m = folium.Map(location=st.session_state['center'], zoom_start=st.session_state['zoom'])

# Adiciona o TileLayer do Google Maps
google_maps_tile = f"https://mt1.google.com/vt/lyrs=r&x={{x}}&y={{y}}&z={{z}}&key={GOOGLE_MAPS_API_KEY}"
folium.TileLayer(tiles=google_maps_tile, attr="Google Maps", name="Google Maps").add_to(m)

# Exibe o mapa inicialmente
with map_placeholder:
    st_folium(m, width=725, height=500)

# Atualiza apenas os pontos de localização no mapa sem recarregar a página inteira
while True:
    # Carregar dados do Firestore
    data_df = get_tracking_data()

    if not data_df.empty:
        # Criar um novo mapa apenas com os marcadores atualizados
        marker_map = folium.Map(location=st.session_state['center'], zoom_start=st.session_state['zoom'], tiles=None)
        google_maps_tile = f"https://mt1.google.com/vt/lyrs=r&x={{x}}&y={{y}}&z={{z}}&key={GOOGLE_MAPS_API_KEY}"
        folium.TileLayer(tiles=google_maps_tile, attr="Google Maps", name="Google Maps").add_to(marker_map)

        # Adicionar marcadores
        for index, row in data_df.iterrows():
            folium.Marker([row['latitude'], row['longitude']], popup=row['status']).add_to(marker_map)

        # Atualizar o mapa no espaço reservado sem recriar o mapa inteiro
        with map_placeholder:
            st_folium(marker_map, width=725, height=500)
    
    # Pausa por um intervalo de tempo antes da próxima atualização
    time.sleep(10)
