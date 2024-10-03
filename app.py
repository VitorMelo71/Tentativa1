import streamlit as st
import streamlit.components.v1 as components
import requests
import folium
from streamlit_folium import st_folium
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

# Função para renderizar o mapa
def render_map(lat, lon):
    # Cria o mapa centrado nas coordenadas fornecidas
    folium_map = folium.Map(location=[lat, lon], zoom_start=15)
    
    # Adiciona o marcador no mapa
    folium.Marker([lat, lon], tooltip="Localização do Veículo").add_to(folium_map)
    
    return folium_map

# Pega a posição inicial para renderizar o mapa
data = get_tracking_data()
if data:
    latest_data = data[0]
    lat = latest_data['latitude']
    lon = latest_data['longitude']

    # Renderiza o mapa inicial
    folium_map = render_map(lat, lon)
    map_placeholder = st_folium(folium_map, width=725, height=500)

# Atualiza a posição do veículo a cada 10 segundos
while True:
    data = get_tracking_data()
    if data:
        latest_data = data[0]
        lat = latest_data['latitude']
        lon = latest_data['longitude']
        
        # Renderiza o mapa atualizado com o marcador movido
        folium_map = render_map(lat, lon)
        map_placeholder = st_folium(folium_map, width=725, height=500)
    
    # Aguarda 10 segundos antes da próxima atualização
    time.sleep(5)
