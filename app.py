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

# Pega a posição inicial para renderizar o mapa
data = get_tracking_data()
if data:
    latest_data = data[0]
    lat = latest_data['latitude']
    lon = latest_data['longitude']

# Função para renderizar o mapa e incluir a função de atualização
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

          window.onload = initMap;

          function updateMarker(lat, lon) {{
            if (typeof marker !== 'undefined' && typeof map !== 'undefined') {{
              var newPosition = new google.maps.LatLng(lat, lon);
              marker.setPosition(newPosition);
              map.setCenter(newPosition);
            }} else {{
              console.error("Mapa ou marcador não está definido corretamente.");
            }}
          }}
        </script>
      </head>
      <body>
        <div id="map" style="width: 100%; height: 500px;"></div>
      </body>
    </html>
""", height=500)

# Função para atualizar a posição do marcador no mapa
def update_map(lat, lon):
    # Injeta código JavaScript que chama a função de atualização do marcador
    components.html(f"""
        <script>
            if (typeof updateMarker === 'function') {{
                updateMarker({lat}, {lon});
            }} else {{
                console.error('Função updateMarker não está definida!');
            }}
        </script>
    """, height=0)

# Atualiza a posição do veículo a cada 10 segundos sem recarregar o mapa
while True:
    data = get_tracking_data()
    if data:
        latest_data = data[0]
        lat = latest_data['latitude']
        lon = latest_data['longitude']
        
        # Atualiza o marcador com as novas coordenadas
        update_map(lat, lon)
    
    # Aguarda 10 segundos para buscar novas coordenadas
    time.sleep(5)
