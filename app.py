import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import tempfile
import folium
from streamlit_folium import st_folium
import time

# Carregar as credenciais do Firebase
firebase_credentials = {
    "type": "service_account",
    "project_id": "banco-gps",
    "private_key_id": "6929102941a72fc9caed116f0f4c1065e5447b0b",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDF8rPDjqWjUhSj\n...",
    "client_email": "firebase-adminsdk-x0vc4@banco-gps.iam.gserviceaccount.com",
    "client_id": "103774825751829582460",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-x0vc4@banco-gps.iam.gserviceaccount.com"
}

# Corrigir quebras de linha na chave privada
firebase_credentials["private_key"] = firebase_credentials["private_key"].replace("\\n", "\n")

# Criar um arquivo temporário para armazenar as credenciais do Firebase
with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
    json.dump(firebase_credentials, temp_file)
    temp_file.flush()

    # Inicializar Firebase com o caminho do arquivo temporário de credenciais
    if not firebase_admin._apps:
        cred = credentials.Certificate(temp_file.name)
        firebase_admin.initialize_app(cred)

# Inicializar o Firestore
db = firestore.client()

st.write("Firebase conectado com sucesso!")
st.title('Rastreamento de Ônibus em Tempo Real')

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

# Função para exibir o mapa no Streamlit com o ícone do ônibus
def exibir_mapa(latitude, longitude):
    mapa = folium.Map(location=[latitude, longitude], zoom_start=15)
    
    # Adicionar o ícone personalizado (imagem do ônibus)
    icon_bus = folium.CustomIcon("https://raw.githubusercontent.com/VitorMelo71/Tentativa1/main/sa.jpg", icon_size=(50, 50))
    
    # Colocar o marcador no mapa
    folium.Marker([latitude, longitude], tooltip="Ônibus", icon=icon_bus).add_to(mapa)
    
    # Renderizar o mapa no Streamlit
    st_folium(mapa, width=725)

# Atualizar localização a cada 10 segundos
while True:
    latitude, longitude, status = buscar_localizacao()
    if latitude is not None and longitude is not None:
        st.write(f"Localização atual: Latitude {latitude}, Longitude {longitude}, Status: {status}")
        exibir_mapa(latitude, longitude)
    else:
        st.write("Aguardando atualização de localização...")

    time.sleep(10)  # Atualizar a cada 10 segundos
