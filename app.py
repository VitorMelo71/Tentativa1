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
st.set_page_config(page_title="Mapa de Rastreamento", layout="centered")

st.title("CEAMAZON - GPS")

# Inicializa o mapa uma única vez
if 'map' not in st.session_state:
    st.session_state['map'] = folium.Map(location=[-1.46906, -48.44755], zoom_start=15)
    st.session_state['vehicle_marker'] = folium.Marker(location=[-1.46906, -48.44755], popup="Veículo")
    st.session_state['vehicle_marker'].add_to(st.session_state['map'])
    st.session_state['zoom'] = 15
    st.session_state['center'] = [-1.46906, -48.44755]

# Função para atualizar apenas a localização do marcador do veículo
def update_vehicle_location():
    data_df = get_tracking_data()

    if not data_df.empty:
        latest_data = data_df.iloc[0]
        new_lat = latest_data['latitude']
        new_lon = latest_data['longitude']

        # Atualiza a posição do marcador
        st.session_state['vehicle_marker'].location = [new_lat, new_lon]

# Exibir o mapa e capturar interações do usuário
map_data = st_folium(st.session_state['map'], width=725, height=500)

# Verificar se há dados de limites no mapa
if map_data and 'bounds' in map_data:
    bounds = map_data['bounds']
    if 'northEast' in bounds and 'southWest' in bounds:
        st.session_state['center'] = [
            (bounds['northEast']['lat'] + bounds['southWest']['lat']) / 2,
            (bounds['northEast']['lng'] + bounds['southWest']['lng']) / 2
        ]
        st.session_state['zoom'] = map_data['zoom']

# Atualiza a localização do veículo a cada 10 segundos
while True:
    update_vehicle_location()
    time.sleep(1)
