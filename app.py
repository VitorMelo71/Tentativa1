import streamlit as st
from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials, firestore
import time

# Chaves de API
FIRESTORE_API_KEY = "AIzaSyCrTdYbECD-ECWNirQBBfPjggedBrRYMeg"
GOOGLE_MAPS_API_KEY = "AIzaSyBJg0w7kTJ2tNWuEeeKgMPSqe97lrFel1w"

# Inicializando o Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("banco-gps-firebase-adminsdk.json")
    firebase_admin.initialize_app(cred)

# Inicializando Firestore
db = firestore.client()

# Função para obter a localização do banco de dados Firestore
def get_vehicle_location():
    doc_ref = db.collection('CoordenadasGPS').document('veiculo')
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        return float(data['latitude']), float(data['longitude'])
    else:
        st.error("Dados de localização não encontrados!")
        return None, None

# Função para criar o mapa do Google
def create_google_map(lat, lon):
    map_html = f'''
    <iframe width="100%" height="500" frameborder="0" style="border:0"
    src="https://www.google.com/maps/embed/v1/place?key={GOOGLE_MAPS_API_KEY}&q={lat},{lon}&zoom=15" allowfullscreen>
    </iframe>
    '''
    return map_html

# Renderiza o mapa uma única vez
lat, lon = get_vehicle_location()
if lat is not None and lon is not None:
    if "map_created" not in st.session_state:
        st.session_state["map_created"] = True
        st.markdown(create_google_map(lat, lon), unsafe_allow_html=True)

# Função para atualizar apenas a localização do veículo
def update_vehicle_marker():
    while True:
        lat, lon = get_vehicle_location()
        if lat is not None and lon is not None:
            # Apenas o marcador será atualizado
            st.session_state["map_created"] = False  # Não recria o mapa
            st.markdown(create_google_map(lat, lon), unsafe_allow_html=True)
        time.sleep(10)  # Atualiza a cada 10 segundos

# Rodando a atualização da posição em loop
update_vehicle_marker()
