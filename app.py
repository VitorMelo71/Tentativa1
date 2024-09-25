import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Carregar as credenciais do Firebase a partir do Secrets do Streamlit
firebase_credentials = st.secrets["firebase_credentials"]

# Inicializar Firebase com as credenciais do Secret Manager
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Função para enviar dados ao Firebase
def enviar_para_firebase(latitude, longitude, status):
    doc_ref = db.collection(u'CoordenadasGPS').document(u'veiculo')
    doc_ref.set({
        u'latitude': latitude,
        u'longitude': longitude,
        u'status': status
    })
    print(f"Dados enviados ao Firebase: Latitude {latitude}, Longitude {longitude}, Status {status}")
