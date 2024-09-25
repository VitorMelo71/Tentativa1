import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import folium
import time
from dotenv import load_dotenv
import os

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Usar as variáveis de ambiente
tkstar_user = os.getenv('TKSTAR_USER')
tkstar_password = os.getenv('TKSTAR_PASSWORD')
firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')

# Inicializar o Firebase com o caminho da credencial
cred = credentials.Certificate(firebase_credentials_path)
initialize_app(cred)


# Inicializar o Firebase
cred = credentials.Certificate("path_to_your_firebase_adminsdk.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Função para obter as últimas coordenadas do Firebase
def get_latest_coordinates():
    doc_ref = db.collection(u'CoordenadasGPS').document(u'veiculo')
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict().get('latitude'), doc.to_dict().get('longitude')
    else:
        return None, None

# Interface do Streamlit
st.title("Rastreamento de Ônibus em Tempo Real")

# Atualiza o mapa a cada 10 segundos
placeholder = st.empty()

while True:
    latitude, longitude = get_latest_coordinates()
    
    if latitude and longitude:
        with placeholder:
            folium_map = folium.Map(location=[latitude, longitude], zoom_start=15)
            folium.Marker([latitude, longitude], popup="Localização do Veículo").add_to(folium_map)
            st.write(folium_map)
    else:
        st.write("Não foram encontradas coordenadas.")

    time.sleep(10)
