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

# Configuração da página
st.set_page_config(page_title="Rastreamento em Tempo Real", layout="centered")

st.title("Mapa de Rastreamento")

# Inicializa o mapa uma única vez
if 'map_initialized' not in st.session_state:
    st.session_state['map_initialized'] = True
    st.session_state['zoom'] = 15
    st.session_state['center'] = [-1.46906, -48.44755]  # Coordenadas padrão

# Cria um espaço reservado para o mapa
map_placeholder = st.empty()

# Exibir o mapa inicialmente
while True:
    # Carregar dados do Firestore
    data_df = get_tracking_data()

    if not data_df.empty:
        # Definir o centro do mapa baseado no primeiro ponto de dados
        st.session_state['center'] = [data_df['latitude'].iloc[0], data_df['longitude'].iloc[0]]

        # Criar a camada de pontos (veículos)
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=data_df,
            get_position='[longitude, latitude]',
            get_color='[200, 30, 0, 160]',
            get_radius=200,
        )

        # Configurar a visualização inicial
        view_state = pdk.ViewState(
            latitude=st.session_state['center'][0],
            longitude=st.session_state['center'][1],
            zoom=st.session_state['zoom'],
            pitch=50,
        )

        # Renderizar o mapa apenas uma vez, atualizando os pontos
        with map_placeholder:
            r = pdk.Deck(layers=[layer], initial_view_state=view_state)
            st.pydeck_chart(r)

    else:
        st.write("Aguardando dados de rastreamento...")

    # Pausar por um intervalo de tempo antes da próxima atualização
    time.sleep(10)
