import streamlit as st
import folium
from streamlit_folium import st_folium
import firebase_admin
from firebase_admin import credentials, firestore

# Configurar a chave de API do Firebase (NÃO RECOMENDADO para produção)
API_KEY = "AIzaSyCrTdYbECD-ECWNirQBBfPjggedBrRYMeg"

# Configurar o Firebase usando a chave de API
def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": "<your_project_id>",
            "private_key_id": "<private_key_id>",
            "private_key": "<private_key>",
            "client_email": "<client_email>",
            "client_id": "<client_id>",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-x0vc4%40banco-gps.iam.gserviceaccount.com"
        })
        firebase_admin.initialize_app(cred)

initialize_firebase()

# Conectar ao Firestore
db = firestore.client()

# Função para criar o mapa no formato responsivo para celular
def create_map():
    m = folium.Map(location=[-15.7801, -47.9292], zoom_start=12)

    # Se o usuário mover o mapa, mantemos a última posição
    st_map = st_folium(m, width=500, height=700)
    return st_map

st.title("Firebase Firestore & Map Example")

# Exemplo de leitura de dados do Firestore
def read_from_firestore():
    users_ref = db.collection(u'users')
    docs = users_ref.stream()

    for doc in docs:
        st.write(f'{doc.id} => {doc.to_dict()}')

# Mostra o mapa no app
st_map = create_map()

# Exemplo de leitura de dados do Firestore
if st.button("Carregar dados do Firestore"):
    read_from_firestore()
