import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json  # Adicionar o módulo JSON para converter o conteúdo

# Carregar as credenciais do Firebase a partir do Secrets do Streamlit
firebase_credentials = st.secrets["firebase_credentials"]

# Converter o conteúdo JSON das credenciais para um dicionário
firebase_credentials_dict = json.loads(json.dumps(firebase_credentials))

# Inicializar Firebase com o dicionário de credenciais
cred = credentials.Certificate(firebase_credentials_dict)
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

# Sua lógica principal continua abaixo
