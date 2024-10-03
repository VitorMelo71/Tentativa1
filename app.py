import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import time

# Configuração da API do Firestore
API_KEY = "YOUR_FIRESTORE_API_KEY"
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

st.title("Mapa de Rastreamento - OpenStreetMap")

# Carrega a imagem da logo e a centraliza
st.image("path/to/your/logo.png", use_column_width=True)

# Definir tamanhos de mapa específicos para computador e celular
if st.session_state.get('device_type', 'computer') == 'computer':
    map_width, map_height = 900, 600  # Mapa maior para computadores
else:
    map_width, map_height = 725, 500  # Mapa menor para celulares

# Inicializa o mapa uma única vez
if 'map_initialized' not in st.session_state:
    st.session_state['map_initialized'] = True
    st.session_state['zoom'] = 15
    st.session_state['center'] = [-1.46906, -48.44755]  # Coordenadas padrão
    st.session_state['map'] = folium.Map(location=st.session_state['center'], zoom_start=st.session_state['zoom'])
    st.session_state['vehicle_marker'] = folium.Marker(location=st.session_state['center'], popup="Veículo")
    st.session_state['vehicle_marker'].add_to(st.session_state['map'])

# Exibe o mapa inicialmente
map_placeholder = st.empty()
with map_placeholder:
    st_folium(st.session_state['map'], width=map_width, height=map_height)

# Atualiza o ponto de localização no mapa sem recarregar a página inteira
def update_vehicle_location():
    data_df = get_tracking_data()

    if not data_df.empty:
        new_lat, new_lon = data_df['latitude'].iloc[0], data_df['longitude'].iloc[0]

        # Atualiza o marcador com a nova posição do veículo
        st.session_state['vehicle_marker'].location = [new_lat, new_lon]

        # Renderiza o mapa atualizado
        map_placeholder.empty()
        with map_placeholder:
            st_folium(st.session_state['map'], width=map_width, height=map_height)

while True:
    update_vehicle_location()
    time.sleep(1)  # Intervalo de atualização
