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

    # Inicializa o mapa do Google Maps com JavaScript
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
        map = new google.maps.Map(document.getElementById("map"),   
 mapOptions);
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

      // Função que atualiza a cada 1 SEGUNDO o marcador do Firebase
      setInterval(function() {{
        fetch("/get_location_data").then(response => response.json()).then(data => {{
          var newLat = data.latitude;
          var newLon = data.longitude;
          updateMarker(newLat, newLon);
        }});
      }}, 1000); // Atualiza a cada 1 segundo
    </script>
  </head>
  <body onload="initMap();">
    <div id="map" style="width: 100%; height: 500px;"></div>
  </body>
</html>
"""

    # Exibe o mapa no componente Streamlit
    components.html(map_html, height=500)

# Backend do Streamlit que retorna os dados de localização do Firebase
@st.cache(ttl=10)
def get_firebase_data():
    data = get_tracking_data()
    if data:
        return {
            'latitude': data[0]['latitude'],
            'longitude': data[0]['longitude']
        }
    return {'latitude': 0, 'longitude': 0}

# Fornece as coordenadas em tempo real para o JavaScript
st.json(get_firebase_data())
