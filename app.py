import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import time

# Configuração da API do Firestore
API_KEY = "AIzaSyCrTdYbECD-ECWNirQBBfPjggedBrRYMeg"
PROJECT_ID = "banco-gps"
COLLECTION = "CoordenadasGPS"

FIRESTORE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/{COLLECTION}?key={API_KEY}"

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

# Configuração da página
st.set_page_config(page_title="Mapa de Rastreamento - OpenStreetMap", layout="centered")

# Carregar a imagem do GitHub
st.image("https://raw.githubusercontent.com/VitorMelo71/Tentativa1/main/sa.jpg", use_column_width=True)

# Inicializa o mapa uma única vez
if 'map_initialized' not in st.session_state:
    st.session_state['map_initialized'] = True
    st.session_state['zoom'] = 15
    st.session_state['center'] = [-1.46906, -48.44755]  # Coordenadas padrão
    st.session_state['map'] = folium.Map(location=st.session_state['center'], zoom_start=st.session_state['zoom'], tiles="OpenStreetMap")

# Cria um espaço reservado para o mapa
map_placeholder = st.empty()

# Exibir o mapa inicialmente
map_placeholder = st_folium(st.session_state['map'], width=725, height=500)

# Função para atualizar a localização do veículo
def update_vehicle_location():
    data_df = get_tracking_data()

    if not data_df.empty:
        # Atualiza a localização do veículo
        new_lat = data_df['latitude'].iloc[0]
        new_lon = data_df['longitude'].iloc[0]

        # Remove o marcador anterior e adiciona um novo marcador
        if 'vehicle_marker' in st.session_state:
            st.session_state['map'].location = [new_lat, new_lon]  # Simplesmente atualiza a localização
        else:
            # Adiciona um novo marcador
            st.session_state['vehicle_marker'] = folium.Marker(location=[new_lat, new_lon], popup="Veículo")
            st.session_state['vehicle_marker'].add_to(st.session_state['map'])

        # Atualiza o mapa no Streamlit sem recriar o mapa inteiro
        with map_placeholder:
            st_folium(st.session_state['map'], width=725, height=500)

# Atualiza a localização do veículo a cada 1 segundo
while True:
    update_vehicle_location()
    time.sleep(1)
    st.experimental_rerun()
