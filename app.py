import streamlit as st
import requests
import time
from streamlit_folium import st_folium
import folium

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

# Inicializa a página do Streamlit
st.set_page_config(page_title="CEAMAZON GPS - Rastreamento", layout="centered")
st.title("CEAMAZON GPS - Rastreamento")

# Obter dados iniciais
data = get_tracking_data()
if data:
    latest_data = data[0]
    lat = latest_data['latitude']
    lon = latest_data['longitude']

    # Criar o mapa inicial com folium
    map_folium = folium.Map(location=[lat, lon], zoom_start=15)
    vehicle_marker = folium.Marker(location=[lat, lon], popup="Veículo", icon=folium.Icon(color="blue"))
    vehicle_marker.add_to(map_folium)

    # Placeholder do mapa no Streamlit
    map_placeholder = st.empty()
    map_placeholder_folium = st_folium(map_folium, height=500, key="initial_map")

    # Atualiza o marcador a cada 10 segundos sem recarregar o mapa
    while True:
        data = get_tracking_data()
        if data:
            latest_data = data[0]
            new_lat = latest_data['latitude']
            new_lon = latest_data['longitude']

            # Remove o marcador antigo
            map_folium.remove_child(vehicle_marker)
            
            # Adiciona o novo marcador com a posição atualizada
            vehicle_marker = folium.Marker(location=[new_lat, new_lon], popup="Veículo", icon=folium.Icon(color="blue"))
            vehicle_marker.add_to(map_folium)

            # Atualiza apenas o marcador no mapa, sem recarregar a posição ou o zoom do mapa
            map_placeholder_folium = st_folium(map_folium, height=500, key="updated_map")

        time.sleep(10)
