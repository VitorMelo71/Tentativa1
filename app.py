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

st.title("Ceamazon")

# Verificar e inicializar o session state para o mapa
if 'zoom' not in st.session_state:
    st.session_state['zoom'] = 15  # Zoom padrão
if 'center' not in st.session_state:
    st.session_state['center'] = [-1.46906, -48.44755]  # Coordenadas padrão

# Carregar dados do Firestore
data_df = get_tracking_data()

if not data_df.empty:
    # Definir o centro do mapa com base nos dados ou usar o estado atual do centro
    center_lat = data_df['latitude'].iloc[0]
    center_lon = data_df['longitude'].iloc[0]
    
    # Criar o mapa centrado no estado atual do mapa ou nos dados
    m = folium.Map(location=st.session_state['center'], zoom_start=st.session_state['zoom'])

    # Adicionar marcador para cada veículo
    for index, row in data_df.iterrows():
        folium.Marker([row['latitude'], row['longitude']], popup=row['status']).add_to(m)

    # Exibir o mapa e capturar a interação do usuário
    map_output = st_folium(m, width=725, height=500)
    
    # Se houver interação do usuário, salvar o novo estado
    if map_output:
        st.session_state['center'] = [map_output['center']['lat'], map_output['center']['lng']]
        st.session_state['zoom'] = map_output['zoom']

else:
    st.write("Aguardando dados de rastreamento...")
