import streamlit.components.v1 as components
import streamlit as st
import requests
import time

# Configuração da API do Firestore e Google Maps
FIRESTORE_API_KEY = "AIzaSyCrTdYbECD-ECWNirQBBfPjggedBrRYMeg"
GOOGLE_MAPS_API_KEY = "AIzaSyBJg0w7kTJ2tNWuEeeKgMPSqe97lrFel1w"
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
            status = fields['status']['stringValue']
            records.append({
                'latitude': latitude,
                'longitude': longitude,
                'status': status
            })
    return records

# Configuração da página para celular
st.set_page_config(page_title="CEAMAZON GPS - Rastreamento", layout="centered")

st.title("CEAMAZON GPS - Rastreamento")

# Inicializa o mapa do Google Maps apenas uma vez
def render_map(lat, lon):
    components.html(f"""
        <html>
          <head>
            <script src="https://maps.googleapis.com/maps/api/js?key={GOOGLE_MAPS_API_KEY}"></script>
            <script>
              var marker;
              var map;

              function initMap() {{
                var mapOptions = {{
                  center: new google.maps.LatLng({lat}, {lon}),
                  zoom: 15,
                  mapTypeId: google.maps.MapTypeId.ROADMAP
                }};
                map = new google.maps.Map(document.getElementById("map"), mapOptions);
                marker = new google.maps.Marker({{
                  position: new google.maps.LatLng({lat}, {lon}),
                  map: map,
                  title: "Localização do Veículo"
                }});
              }}

              window.updateMarker = function(lat, lon) {{
                var newPosition = new google.maps.LatLng(lat, lon);
                marker.setPosition(newPosition);
              }};

              window.centerMap = function(lat, lon) {{
                map.setCenter(new google.maps.LatLng(lat, lon));
              }};
            </script>
          </head>
          <body onload="initMap()">
            <div id="map" style="width: 100%; height: 500px;"></div>
          </body>
        </html>
    """, height=500)

# Pega a posição inicial para renderizar o mapa
data = get_tracking_data()

if data:
    latest_data = data[0]
    render_map(latest_data['latitude'], latest_data['longitude'])

# Adiciona o botão para centralizar no veículo
if st.button("Centralizar no veículo"):
    if data:
        latest_data = data[0]
        # Centraliza o mapa na posição atual do veículo
        components.html(f"""
            <script>
                centerMap({latest_data['latitude']}, {latest_data['longitude']});
            </script>
        """, height=0)

# Atualiza a posição do veículo a cada 10 segundos
while True:
    data = get_tracking_data()
    if data:
        latest_data = data[0]
        # Atualiza o marcador sem recarregar o mapa
        components.html(f"""
            <script>
                updateMarker({latest_data['latitude']}, {latest_data['longitude']});
            </script>
        """, height=0)
    time.sleep(10)
