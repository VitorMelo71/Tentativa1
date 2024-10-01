import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
import folium
from streamlit_folium import st_folium
import time
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Carregar as credenciais do Firebase a partir das variáveis de ambiente
firebase_credentials = {
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
}

# Inicializar Firebase com as credenciais carregadas
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)

# Inicializar o Firestore
db = firestore.client()

st.write("Firebase conectado com sucesso!")

# Função para buscar a última localização do Firestore
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

# Função para exibir o mapa no Streamlit com o ícone do ônibus arredondado
def exibir_mapa(latitude, longitude):
    mapa = folium.Map(location=[latitude, longitude], zoom_start=15)

    # Adicionar o ícone personalizado arredondado com CSS
    html = f"""
    <div style="border-radius: 50%; overflow: hidden; width: 30px; height: 30px;">
        <img src="https://raw.githubusercontent.com/VitorMelo71/Tentativa1/main/sa.jpg" style="width: 100%; height: 100%;">
    </div>
    """
    
    iframe = folium.IFrame(html=html, width=60, height=60)
    popup = folium.Popup(iframe, max_width=2650)

    folium.Marker(
        location=[latitude, longitude],
        popup=popup,
        tooltip="Ônibus"
    ).add_to(mapa)
    
    st_folium(mapa, width=300)

st.title('Circular UFPA')

# Atualizar localização a cada 10 segundos
while True:
    latitude, longitude, status = buscar_localizacao()
    if latitude is not None and longitude is not None:
        st.write(f"Status: {status}")
        exibir_mapa(latitude, longitude)
    else:
        st.write("Aguardando atualização de localização...")

    time.sleep(10)  # Atualizar a cada 10 segundos
