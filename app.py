import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import streamlit.components.v1 as components

# Inicializa o Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("banco-gps-firebase-adminsdk.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Função para obter a posição do veículo
def get_vehicle_position():
    doc_ref = db.collection('CoordenadasGPS').document('veiculo')
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        return lat, lon
    else:
        st.write("Documento não encontrado no Firestore")
        return None, None

# Obtém a latitude e longitude do Firestore
lat, lon = get_vehicle_position()

# Verifique os valores carregados
st.write(f"Latitude: {lat}, Longitude: {lon}")

if lat is not None and lon is not None:
    # Exibe o mapa com a posição inicial
    map_html = generate_map_html(lat, lon)
    components.html(map_html, height=500)

    # Atualiza a posição do marcador dinamicamente
    components.html(f"""
    <script>
        updateMarkerPosition({lat}, {lon});
    </script>
    """, height=0, width=0)
else:
    st.write("Não foi possível carregar a posição do veículo")
