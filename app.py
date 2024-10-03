import streamlit as st
import streamlit.components.v1 as components
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
    map_html = f"""
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
            map.setCenter(newPosition);
          }}
        </script>
      </head>
      <body onload="initMap();">
        <div id="map" style="width: 100%; height: 500px;"></div>
      </body>
    </html>
    """
    components.html(map_html, height=500)

# Obtém dados iniciais e renderiza o mapa
data = get_tracking_data()

if data:
    latest_data = data[0]
    lat = latest_data['latitude']
    lon = latest_data['longitude']

    # Renderiza o mapa inicialmente
    render_map(lat, lon)

    # Atualiza a posição do veículo a cada 10 segundos
    while True:
        data = get_tracking_data()
        if data:
            latest_data = data[0]
            lat = latest_data['latitude']
            lon = latest_data['longitude']
            components.html(f"<script>window.updateMarker({lat}, {lon});</script>", height=0)
        time.sleep(5)
