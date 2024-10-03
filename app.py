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
    st.session_state['vehicle_marker'] = None  # Inicializa o marcador como None

# Função para atualizar apenas o marcador do veículo
def update_vehicle_location():
    # Obter os dados de rastreamento
    data_df = get_tracking_data()

    if not data_df.empty:
        # Pega a primeira localização do veículo
        latest_data = data_df.iloc[0]
        new_lat = latest_data['latitude']
        new_lon = latest_data['longitude']

        # Remove o marcador antigo, se existir
        if st.session_state['vehicle_marker'] is not None:
            st.session_state['map'].remove_child(st.session_state['vehicle_marker'])

        # Adiciona um novo marcador na posição atualizada
        st.session_state['vehicle_marker'] = folium.Marker(location=[new_lat, new_lon], popup="Veículo")
        st.session_state['vehicle_marker'].add_to(st.session_state['map'])

# Exibe o mapa inicial e atualiza o marcador do veículo
while True:
    update_vehicle_location()
    
    # Renderiza o mapa com o marcador atualizado
    map_placeholder = st_folium(st.session_state['map'], width=725, height=500)
    
    time.sleep(10)
