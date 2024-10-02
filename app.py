from dotenv import load_dotenv
import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import tempfile
import folium
from streamlit_folium import st_folium
import time

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Carregar os segredos do Firebase do ambiente do Streamlit
firebase_credentials = {
    "type": "service_account",
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
}

# Inicializar o Firebase com as credenciais do ambiente
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
