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

# Configuração da página
st.set_page_config(page_title="CEAMAZON GPS - Rastreamento", layout="centered")

# Modo dark ao fundo do site
st.markdown("""
    <style>
    body {
        background-color: #121212;
    }
    .stText, .stMarkdown, .stButton > button {
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.title("CEAMAZON GPS - Rastreamento")

# Função para renderizar o mapa com JavaScript e o marcador
def render_map(lat, lon):
    map_code = f"""
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
            window.map = map;
            window.marker = marker;
          }}

          function updateMarker(lat, lon) {{
            if (window.marker) {{
              var newPosition = new google.maps.LatLng(lat, lon);
              window.marker.setPosition(newPosition);
              window.map.setCenter(newPosition);
            }}
          }}

          window.initMap = initMap;
          window.updateMarker = updateMarker;
        </script>
      </head>
      <body onload="initMap()" style="background-color: #121212;">
        <div id="map" style="width: 100%; height: 500px;"></div>
      </body>
    </html>
    """
    components.html(map_code, height=500)

# Carrega o mapa apenas uma vez
data = get_tracking_data()
if data:
    latest_data = data[0]
    render_map(latest_data['latitude'], latest_data['longitude'])

# Configuração para atualizar o marcador a cada 10 segundos
update_interval = 10  # segundos

# Loop de atualização do marcador
while True:
    data = get_tracking_data()
    if data:
        latest_data = data[0]
        update_code = f"""
        <script>
            updateMarker({latest_data['latitude']}, {latest_data['longitude']});
        </script>
        """
        components.html(update_code, height=0)  # Apenas atualiza o marcador sem renderizar um novo mapa
    time.sleep(update_interval)
