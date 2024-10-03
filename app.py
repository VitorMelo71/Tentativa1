import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import time
import pyttsx3
import math

# Configuração da API do Firestore
API_KEY = "AIzaSyCrTdYbECD-ECWNirQBBfPjggedBrRYMeg"
PROJECT_ID = "banco-gps"
COLLECTION = "CoordenadasGPS"

FIRESTORE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/{COLLECTION}?key={API_KEY}"

# Configurar a síntese de voz
engine = pyttsx3.init()

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

# Função para emitir uma notificação por voz
def notify_gate3():
    engine.say("Você chegou ao portão 3")
    engine.runAndWait()

# Função para calcular a distância entre dois pontos geográficos usando a fórmula de Haversine
def calculate_distance(lat1, lon1, lat2, lon2):
    # Converter graus para radianos
    R = 6371  # Raio da Terra em quilômetros
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c  # Distância em quilômetros
    return distance

# Função para verificar se o veículo está no Portão 3
def check_gate3(lat, lon):
    gate3_lat = -1.47266
    gate3_lon = -48.45137
    threshold = 0.0001  # Definir uma distância mínima para considerar que chegou

    if abs(lat - gate3_lat) < threshold and abs(lon - gate3_lon) < threshold:
        notify_gate3()

# Configuração da página
st.set_page_config(page_title="Mapa de Rastreamento", layout="centered")

st.title("Mapa de Rastreamento - OpenStreetMap")

# Inicializa o mapa uma única vez
if 'map' not in st.session_state:
    st.session_state['map'] = folium.Map(location=[-1.46906, -48.44755], zoom_start=15)
    st.session_state['vehicle_marker'] = folium.Marker(location=[-1.46906, -48.44755], popup="Veículo")
    st.session_state['vehicle_marker'].add_to(st.session_state['map'])
    st.session_state['zoom'] = 15
    st.session_state['center'] = [-1.46906, -48.44755]

# Pede ao usuário para inserir suas coordenadas
user_lat = st.number_input("Insira sua latitude", value=-1.46906)
user_lon = st.number_input("Insira sua longitude", value=-48.44755)

# Função para atualizar apenas a localização do marcador do veículo
def update_vehicle_location():
    data_df = get_tracking_data()

    if not data_df.empty:
        latest_data = data_df.iloc[0]
        new_lat = latest_data['latitude']
        new_lon = latest_data['longitude']

        # Atualiza a posição do marcador
        st.session_state['vehicle_marker'].location = [new_lat, new_lon]

        # Verifica se o veículo está no Portão 3
        check_gate3(new_lat, new_lon)

        # Calcula a distância entre o veículo e o usuário
        distance = calculate_distance(user_lat, user_lon, new_lat, new_lon)
        st.write(f"O veículo está a {distance:.2f} km de você.")

# Exibir o mapa e capturar interações do usuário
map_data = st_folium(st.session_state['map'], width=725, height=500)

# Verificar se há dados de limites no mapa
if map_data and 'bounds' in map_data:
    bounds = map_data['bounds']
    if 'northEast' in bounds and 'southWest' in bounds:
        st.session_state['center'] = [
            (bounds['northEast']['lat'] + bounds['southWest']['lat']) / 2,
            (bounds['northEast']['lng'] + bounds['southWest']['lng']) / 2
        ]
        st.session_state['zoom'] = map_data['zoom']

# Atualiza a localização do veículo a cada 10 segundos
while True:
    update_vehicle_location()
    time.sleep(10)
