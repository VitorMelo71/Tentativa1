import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import folium
from streamlit_folium import st_folium
import time

# Carregar as credenciais do Firebase a partir do Secrets do Streamlit
firebase_credentials = st.secrets["firebase_credentials"]

# Inicializar Firebase (somente uma vez)
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)

# Inicializar o Firestore
db = firestore.client()

# Função para buscar a localização do Firestore
def buscar_localizacao():
    doc_ref = db.collection(u'CoordenadasGPS').document(u'veiculo')
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        status = data.get('status')
        return float(latitude), float(longitude), status
    else:
        return None, None, None

# Função para exibir o mapa
def exibir_mapa(latitude, longitude):
    mapa = folium.Map(location=[latitude, longitude], zoom_start=15)
    folium.Marker([latitude, longitude], tooltip="Ônibus").add_to(mapa)
    st_folium(mapa, width=725)

# App principal
st.title('Rastreamento de Ônibus em Tempo Real')

# Atualizar localização a cada 10 segundos
while True:
    latitude, longitude, status = buscar_localizacao()
    if latitude is not None and longitude is not None:
        st.write(f"Localização atual: Latitude {latitude}, Longitude {longitude}, Status: {status}")
        exibir_mapa(latitude, longitude)
    else:
        st.write("Aguardando atualização de localização...")
    
    time.sleep(10)  # Atualizar a cada 10 segundos
