import streamlit as st
import streamlit.components.v1 as components
import time

# Configuração da API do Google Maps
GOOGLE_MAPS_API_KEY = "AIzaSyBJg0w7kTJ2tNWuEeeKgMPSqe97lrFel1w"

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

# Inicializa a latitude e longitude
if 'lat' not in st.session_state:
    st.session_state.lat = -1.46906
if 'lon' not in st.session_state:
    st.session_state.lon = -48.44755

# Gera o mapa inicial
map_html = generate_map_html(st.session_state.lat, st.session_state.lon)
components.html(map_html, height=500)

# Função para atualizar a posição do veículo
def update_position():
    st.session_state.lat += 0.001  # Simula uma nova posição
    st.session_state.lon += 0.001  # Simula uma nova posição

# Botão para atualizar manualmente
if st.button('Atualizar Posição do Veículo'):
    update_position()

# Atualização automática a cada 10 segundos
st_autorefresh(interval=10 * 1000, key="refresh")

# Atualiza a posição do marcador dinamicamente
components.html(f"""
<script>
    updateMarkerPosition({st.session_state.lat}, {st.session_state.lon});
</script>
""", height=0, width=0)
