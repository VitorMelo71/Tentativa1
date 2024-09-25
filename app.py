import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import tempfile

# Carregar as credenciais do Firebase a partir do Secrets do Streamlit
firebase_credentials = st.secrets["firebase_credentials"]

# Verificar se as credenciais são um dicionário e convertê-las, se necessário
if isinstance(firebase_credentials, dict):
    credentials_dict = firebase_credentials
else:
    credentials_dict = dict(firebase_credentials)

# Criar um arquivo temporário para armazenar as credenciais do Firebase
with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
    json.dump(credentials_dict, temp_file)
    temp_file.flush()

    # Inicializar Firebase com o caminho do arquivo temporário de credenciais
    if not firebase_admin._apps:  # Verificar se o Firebase já foi inicializado
        cred = credentials.Certificate(temp_file.name)
        firebase_admin.initialize_app(cred)

# Inicializar o Firestore
db = firestore.client()

st.write("Firebase conectado com sucesso!")
