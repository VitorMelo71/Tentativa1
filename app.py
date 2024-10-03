import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import time

# Configuração da API do Firestore
FIRESTORE_API_KEY = "AIzaSyCrTdYbECD-ECWNirQBBfPjggedBrRYMeg"
PROJECT_ID = "banco-gps"
COLLECTION = "CoordenadasGPS"
FIRESTORE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/{COLLECTION}?key={FIRESTORE_API_KEY}"

# Função para buscar dados do Firestore via API REST
def get_tracking_data():
    response = requests.get(FIRESTORE_URL)
    data = response.json()

    records = []
    if 'documents' in data:
        for doc in data['documents']:
            fields = doc['fields']
            latitude = float(fields['latitude']['stringValue'])
            longitude = float(fields['longitude']['stringValue'])
            records.append({
                'latitude': latitude,
                'longitude': longitude
            })
    return records

# Configuração da página
st.set_page_config(page_title="CEAMAZON GPS - Rastreamento", layout="centered")

st.title("CEAMAZON GPS - Rastreamento")

# Função que renderiza o mapa no Streamlit
def render_map(lat, lon):
    # Cria o mapa Folium
    folium_map = folium.Map(location=[lat, lon], zoom_start=15)
    
    # Adiciona o marcador ao mapa
    folium.Marker([lat, lon], tooltip="Localização do Veículo").add_to(folium_map)
    
    return folium_map

# Obtém dados iniciais e renderiza o mapa
data = get_tracking_data()

if data:
    latest_data = data[0]
    lat = latest_data['latitude']
    lon = latest_data['longitude']

    # Renderiza o mapa com a posição inicial
    folium_map = render_map(lat, lon)
    map_placeholder = st.empty()
    map_placeholder = st_folium(folium_map, height=500, width=700)

    # Atualiza a posição do veículo a cada 10 segundos
    while True:
        data = get_tracking_data()
        if data:
            latest_data = data[0]
            lat = latest_data['latitude']
            lon = latest_data['longitude']

            # Recria o mapa com a nova posição
            folium_map = render_map(lat, lon)
            
            # Atualiza o mapa no Streamlit
            map_placeholder = st_folium(folium_map, height=500, width=700)
        
        time.sleep(10)
