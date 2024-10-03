import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium

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

# Configuração da página para celular (iPhone 11)
st.set_page_config(page_title="Rastreamento em Tempo Real", layout="centered")

st.title("Mapa de Rastreamento - OpenStreetMap")

# Inicializa o mapa apenas uma vez e mantém a posição e o zoom
if 'map_initialized' not in st.session_state:
    st.session_state['zoom'] = 15
    st.session_state['center'] = [-1.46906, -48.44755]  # Coordenadas padrão
    st.session_state['map_initialized'] = True

# Cria um espaço reservado para o mapa
map_placeholder = st.empty()

# Função para atualizar o mapa
def update_map():
    # Carregar dados do Firestore
    data_df = get_tracking_data()

    # Inicializa o mapa
    m = folium.Map(location=st.session_state['center'], zoom_start=st.session_state['zoom'], tiles="OpenStreetMap")

    if not data_df.empty:
        # Insere novos marcadores com base na nova localização
        for index, row in data_df.iterrows():
            folium.Marker([row['latitude'], row['longitude']], popup=row['status']).add_to(m)

    # Exibe o mapa
    with map_placeholder:
        st_folium(m, width=725, height=500)

# Atualiza o mapa a cada 10 segundos sem bloquear o fluxo da aplicação
st_autorefresh(interval=10 * 1000, limit=None, key="autorefresh")

# Chama a função de atualização do mapa
update_map()
