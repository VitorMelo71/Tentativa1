import streamlit as st
import streamlit.components.v1 as components
import time

# Configuração da API do Google Maps
GOOGLE_MAPS_API_KEY = "AIzaSyAvBYntkiyjBNpU96UdMSoD5cavd3lqQtY"

# Função para gerar o HTML/JS do Google Maps
def generate_map_html(lat, lon):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://maps.googleapis.com/maps/api/js?key={GOOGLE_MAPS_API_KEY}"></script>
        <script>
            var map;
            var marker;

            function initMap() {{
                var center = {{lat: {lat}, lng: {lon}}};
                map = new google.maps.Map(document.getElementById('map'), {{
                    zoom: 15,
                    center: center
                }});
                marker = new google.maps.Marker({{
                    position: center,
                    map: map,
                    title: 'Veículo'
                }});
            }}

            function updateMarkerPosition(lat, lon) {{
                var newLatLng = new google.maps.LatLng(lat, lon);
                marker.setPosition(newLatLng);
                map.setCenter(newLatLng);
            }}

            window.initMap = initMap;
        </script>
    </head>
    <body onload="initMap()">
        <div id="map" style="width: 100%; height: 500px;"></div>
    </body>
    </html>
    """

# Renderiza o mapa inicial
st.set_page_config(page_title="CEAMAZON GPS", layout="centered")
st.title("CEAMAZON GPS - Rastreamento")

# Inicializa a latitude e longitude
lat = -1.46906
lon = -48.44755

# Gera o mapa inicial
map_html = generate_map_html(lat, lon)
components.html(map_html, height=500)

# Simula atualizações de posição
def update_position(lat, lon):
    # Atualiza a posição do veículo periodicamente
    for i in range(10):
        lat += 0.001  # Simula uma nova posição
        lon += 0.001  # Simula uma nova posição
        # Passa a nova posição ao mapa via Streamlit custom components
        components.html(f"""
        <script>
            updateMarkerPosition({lat}, {lon});
        </script>
        """, height=0, width=0)
        time.sleep(5)

# Chama a função para atualizar a posição
update_position(lat, lon)
