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
st.set_page_config(page_title="Rastreamento em Tempo Real", layout="centered")

st.title("Mapa de Rastreamento - OpenStreetMap")

# Inicializa o mapa uma única vez
if 'map_initialized' not in st.session_state:
    st.session_state['map_initialized'] = True
    st.session_state['zoom'] = 15
    st.session_state['center'] = [-1.46906, -48.44755]  # Coordenadas padrão
    st.session_state['map'] = folium.Map(location=st.session_state['center'], zoom_start=st.session_state['zoom'])

# Adiciona um marcador de veículo inicial (ajustável)
if 'vehicle_marker' not in st.session_state:
    st.session_state['vehicle_marker'] = folium.Marker(location=st.session_state['center'], popup="Veículo")
    st.session_state['vehicle_marker'].add_to(st.session_state['map'])

# Cria um espaço reservado para o mapa
map_placeholder = st.empty()

# Exibir o mapa inicialmente
output = st_folium(st.session_state['map'], width=725, height=500, key="main_map")

# Função para atualizar a localização do veículo
def update_vehicle_location():
    # Simula a obtenção de novas coordenadas
    new_lat, new_lon = -1.469, -48.448  # Simule isso como vindo do Firestore
    
    # Captura o estado atual do mapa (posição e zoom)
    current_center = output['center']
    current_zoom = output['zoom']
    
    # Atualiza a posição do marcador
    st.session_state['vehicle_marker'].location = [new_lat, new_lon]

    # Recria o mapa preservando o centro e o zoom
    updated_map = folium.Map(location=current_center, zoom_start=current_zoom)
    st.session_state['vehicle_marker'].add_to(updated_map)
    
    # Atualiza o mapa no espaço reservado
    with map_placeholder:
        st_folium(updated_map, width=725, height=500, key="updated_map")

# Atualiza a localização do veículo a cada 10 segundos
while True:
    update_vehicle_location()
    time.sleep(10)
