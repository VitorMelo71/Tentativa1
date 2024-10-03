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

st.title("Mapa de Rastreamento - OpenStreetMap")

# Inicializa o mapa uma única vez
if 'map' not in st.session_state:
    st.session_state['map'] = folium.Map(location=[-1.46906, -48.44755], zoom_start=15)
    st.session_state['vehicle_marker'] = folium.Marker(location=[-1.46906, -48.44755], popup="Veículo")
    st.session_state['vehicle_marker'].add_to(st.session_state['map'])

# Função para atualizar apenas a localização do marcador do veículo
def update_vehicle_location():
    # Obter os dados de rastreamento
    data_df = get_tracking_data()

    if not data_df.empty:
        # Pega a primeira localização do veículo
        latest_data = data_df.iloc[0]
        new_lat = latest_data['latitude']
        new_lon = latest_data['longitude']

        # Atualiza a posição do marcador
        st.session_state['vehicle_marker'].location = [new_lat, new_lon]

# Renderizar o mapa apenas uma vez
map_placeholder = st.empty()
with map_placeholder:
    st_folium(st.session_state['map'], width=725, height=500)

# Atualiza a localização do veículo sem renderizar novamente o mapa
while True:
    update_vehicle_location()
    
    # Atualiza o estado do marcador no mapa
    st.session_state['vehicle_marker'].location = st.session_state['vehicle_marker'].location

    # Espera 10 segundos para a próxima atualização
    time.sleep(10)
