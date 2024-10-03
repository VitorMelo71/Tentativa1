import streamlit as st
import folium
from streamlit_folium import st_folium
import time
import requests
import pandas as pd

# Configuração da API do Firestore
API_KEY = "Sua API"
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

# Inicializa o mapa apenas uma vez
if 'map_initialized' not in st.session_state:
    st.session_state['zoom'] = 15
    st.session_state['center'] = [-1.46906, -48.44755]
    st.session_state['map_initialized'] = True
    st.session_state['vehicle_marker'] = None

st.title("Mapa de Rastreamento - OpenStreetMap")

# Botão para ir para a localização do veículo
if st.button("Ir para a localização do ônibus"):
    tracking_data = get_tracking_data()
    if not tracking_data.empty:
        # Atualiza o centro do mapa para a posição do veículo
        st.session_state['center'] = [tracking_data['latitude'].iloc[0], tracking_data['longitude'].iloc[0]]
        st.session_state['zoom'] = 15

# Inicializa o mapa
m = folium.Map(location=st.session_state['center'], zoom_start=st.session_state['zoom'], tiles="OpenStreetMap")

# Atualiza o ponto de localização no mapa
tracking_data = get_tracking_data()

if not tracking_data.empty:
    if st.session_state['vehicle_marker']:
        # Remove o marcador anterior
        st.session_state['vehicle_marker'].pop().remove()

    # Adiciona o novo marcador
    st.session_state['vehicle_marker'] = folium.Marker(
        [tracking_data['latitude'].iloc[0], tracking_data['longitude'].iloc[0]],
        popup="Ônibus"
    ).add_to(m)

# Exibe o mapa uma única vez e o mantém estático
st_folium(m, key="map", width=1000, height=1000)
