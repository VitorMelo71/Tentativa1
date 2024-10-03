import streamlit as st
import streamlit.components.v1 as components
import requests

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

# Configuração da página para celular
st.set_page_config(page_title="CEAMAZON GPS - Rastreamento", layout="centered")

st.title("CEAMAZON GPS - Rastreamento")

# Pega a posição inicial para renderizar o mapa
data = get_tracking_data()

if data:
    latest_data = data[0]
    lat = latest_data['latitude']
    lon = latest_data['longitude']

    # Inicializa o mapa do Google Maps uma vez
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

          function updateMarker(lat, lon) {{
            var newPosition = new google.maps.LatLng(lat, lon);
            marker.setPosition(newPosition);
            map.setCenter(newPosition);
          }}

          window.updateMarker = updateMarker;  // Define a função global para ser chamada externamente
        </script>
      </head>
      <body onload="initMap()">
        <div id="map" style="width: 100%; height: 500px;"></div>
      </body>
    </html>
    """

    components.html(map_html, height=500)

    # Atualiza o marcador automaticamente a cada 10 segundos
    st_autorefresh(interval=10*1000, limit=None)

    # Atualiza os dados e envia o novo lat/lon para o JavaScript
    new_data = get_tracking_data()
    if new_data:
        latest_data = new_data[0]
        new_lat = latest_data['latitude']
        new_lon = latest_data['longitude']
        update_js = f"""
        <script>
            window.updateMarker({new_lat}, {new_lon});
        </script>
        """
        components.html(update_js, height=0)
