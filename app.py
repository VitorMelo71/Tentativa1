import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
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

# Configuração da página para celular (iPhone 11)
st.set_page_config(page_title="Rastreamento em Tempo Real", layout="centered")

st.title("Mapa de Rastreamento")

# Inicializa um dataframe vazio
data_df = pd.DataFrame(columns=['latitude', 'longitude', 'status'])

# Intervalo de atualização
update_interval = 10  # segundos

while True:
    # Carregar dados do Firestore
    data_df = get_tracking_data()

    if not data_df.empty:
        # Mostrar o mapa se houver dados
        midpoint = (data_df['latitude'].astype(float).mean(), data_df['longitude'].astype(float).mean())
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(
                latitude=midpoint[0],
                longitude=midpoint[1],
                zoom=14,
                pitch=50,
            ),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',
                    data=data_df,
                    get_position='[longitude, latitude]',
                    get_color='[200, 30, 0, 160]',
                    get_radius=200,
                ),
            ],
        ))
    else:
        st.write("Aguardando dados de rastreamento...")

    # Pausa para atualizar
    time.sleep(update_interval)
