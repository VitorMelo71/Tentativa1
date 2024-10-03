import streamlit as st
import googlemaps
import firebase_admin
from firebase_admin import credentials, firestore
import time

# Configuração da API do Firestore e Google Maps
FIRESTORE_API_KEY = "AIzaSyCrTdYbECD-ECWNirQBBfPjggedBrRYMeg"
GOOGLE_MAPS_API_KEY = "AIzaSyBJg0w7kTJ2tNWuEeeKgMPSqe97lrFel1w"
PROJECT_ID = "banco-gps"
COLLECTION = "CoordenadasGPS"
FIRESTORE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/{COLLECTION}"

# Inicializando Firestore
db = firestore.client()

st.title("CEAMAZON GPS - Rastreamento")

# Função para buscar as coordenadas do veículo no Firestore
def get_vehicle_location():
    doc_ref = db.collection(COLLECTION).document("onibus1")
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        return data.get("latitude"), data.get("longitude")
    else:
        return None, None

# Configurando o mapa do Google Maps
def render_map(latitude, longitude):
    st.components.v1.html(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Google Maps</title>
            <script src="https://maps.googleapis.com/maps/api/js?key={GOOGLE_MAPS_API_KEY}"></script>
            <script>
                function initMap() {{
                    var location = {{lat: {latitude}, lng: {longitude}}};
                    var map = new google.maps.Map(document.getElementById('map'), {{
                        zoom: 16,
                        center: location
                    }});
                    
                    var icon = {{
                        url: "https://raw.githubusercontent.com/VitorMelo71/Tentativa1/main/sa.png",  // URL da imagem de ícone do ônibus
                        scaledSize: new google.maps.Size(40, 40)  // Tamanho do ícone
                    }};
                    
                    var marker = new google.maps.Marker({{
                        position: location,
                        map: map,
                        icon: icon
                    }});
                }}
            </script>
        </head>
        <body onload="initMap()">
            <div id="map" style="width: 100%; height: 500px;"></div>
        </body>
        </html>
    """, height=500)

# Atualizando a posição do veículo no mapa
latitude, longitude = get_vehicle_location()

if latitude and longitude:
    render_map(latitude, longitude)
else:
    st.error("Não foi possível buscar a localização do veículo.")

# Atualização automática a cada 10 segundos
if st.button("Atualizar Posição do Veículo"):
    time.sleep(10)
    latitude, longitude = get_vehicle_location()
    render_map(latitude, longitude)
