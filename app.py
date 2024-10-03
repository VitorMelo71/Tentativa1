import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import folium_static
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

# Carregar a imagem do logotipo
st.image("https://raw.githubusercontent.com/VitorMelo71/Tentativa1/main/sa.jpg", use_column_width=True)

# Inicializa o mapa uma única vez
if 'map_initialized' not in st.session_state:
    st.session_state['map_initialized'] = True
    st.session_state['zoom'] = 15
    st.session_state['center'] = [-1.46906, -48.44755]  # Coordenadas padrão
    st.session_state['map'] = folium.Map(location=st.session_state['center'], zoom_start=st.session_state['zoom'], tiles="OpenStreetMap")
    st.session_state['vehicle_marker'] = folium.Marker(location=st.session_state['center'], popup="Veículo")
    st.session_state['vehicle_marker'].add_to(st.session_state['map'])

# Função para atualizar a localização do veículo
def update_vehicle_location():
    data_df = get_tracking_data()

    if not data_df.empty:
        # Atualiza a localização do veículo
        new_lat = data_df['latitude'].iloc[0]
        new_lon = data_df['longitude'].iloc[0]

        # Atualiza o marcador para a nova posição
        st.session_state['vehicle_marker'].location = [new_lat, new_lon]

        # Se o botão for clicado, centraliza o mapa na localização do veículo
        if st.session_state.get('center_on_vehicle', False):
            st.session_state['map'].location = [new_lat, new_lon]

# Cria um espaço reservado para o mapa e exibe-o
map_placeholder = st.empty()

# Botão para centralizar o mapa na localização do ônibus
if st.button("Ir para a localização do ônibus"):
    st.session_state['center_on_vehicle'] = True
else:
    st.session_state['center_on_vehicle'] = False

# Exibir o mapa inicialmente
with map_placeholder:
    folium_static(st.session_state['map'], width=1000, height=1000)

# Atualiza a localização do veículo a cada 1 segundo
while True:
    update_vehicle_location()

    # Atualiza o mapa no Streamlit sem recriar todo o mapa
    with map_placeholder:
        folium_static(st.session_state['map'], width=1000, height=1000)

    time.sleep(1)
