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

st.title("CEAMAZON GPS")

# Inicializa o mapa uma única vez
if 'map' not in st.session_state:
    st.session_state['zoom'] = 15
    st.session_state['center'] = [-1.46906, -48.44755]  # Coordenadas padrão
    # Criação inicial do mapa
    st.session_state['map'] = folium.Map(location=st.session_state['center'], zoom_start=st.session_state['zoom'], tiles="OpenStreetMap")
    # Adiciona um marcador inicial
    st.session_state['vehicle_marker'] = folium.Marker(location=st.session_state['center'], popup="Veículo")
    st.session_state['vehicle_marker'].add_to(st.session_state['map'])

# Função para atualizar a posição do veículo
def update_vehicle_location():
    data_df = get_tracking_data()

    if not data_df.empty:
        # Obtém a última posição do veículo
        latest_data = data_df.iloc[0]
        new_lat = latest_data['latitude']
        new_lon = latest_data['longitude']

        # Remove o marcador anterior
        st.session_state['map'] = folium.Map(location=[new_lat, new_lon], zoom_start=st.session_state['zoom'], tiles="OpenStreetMap")
        # Adiciona o novo marcador
        folium.Marker(location=[new_lat, new_lon], popup="Veículo").add_to(st.session_state['map'])

        # Renderiza o mapa atualizado
        st_folium(st.session_state['map'], width=725, height=500)

    else:
        st.write("Aguardando dados de rastreamento...")

# Exibe o mapa uma vez
st_folium(st.session_state['map'], width=725, height=500)

# Atualiza a localização do veículo a cada 10 segundos
while True:
    update_vehicle_location()
    time.sleep(5)
