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

st.title("Mapa de Rastreamento")

# Atualização automática a cada 10 segundos
st.experimental_set_query_params(interval=10)  # Define o intervalo de atualização (em segundos)

# Carregar dados do Firestore
data_df = get_tracking_data()

if not data_df.empty:
    # Criar o mapa centrado no primeiro ponto de dados
    m = folium.Map(location=[data_df['latitude'].iloc[0], data_df['longitude'].iloc[0]], zoom_start=15)

    # Adicionar marcador para cada veículo
    for index, row in data_df.iterrows():
        folium.Marker([row['latitude'], row['longitude']], popup=row['status']).add_to(m)

    # Exibir o mapa
    st_folium(m, width=725)

else:
    st.write("Aguardando dados de rastreamento...")
