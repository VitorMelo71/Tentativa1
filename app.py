import streamlit as st
import os
import json
import firebase_admin
from firebase_admin import credentials

# Carregando o segredo FIREBASE_CREDENTIALS da variável de ambiente
firebase_credentials_str = os.getenv("FIREBASE_CREDENTIALS")

# Verifica se o segredo foi carregado corretamente
if firebase_credentials_str is None:
    st.error("O segredo FIREBASE_CREDENTIALS não está carregado.")
else:
    st.write("Segredo FIREBASE_CREDENTIALS carregado com sucesso.")

    try:
        # Tente carregar o conteúdo como um JSON
        firebase_credentials = json.loads(firebase_credentials_str)
        st.write("Firebase credentials carregadas corretamente.")
        
        # Aqui você pode inicializar o Firebase com as credenciais carregadas
        # Exemplo:
        # cred = credentials.Certificate(firebase_credentials)
        # firebase_admin.initialize_app(cred)

    except json.JSONDecodeError:
        st.error("Erro ao decodificar o segredo FIREBASE_CREDENTIALS como JSON.")
    
# Recuperar o conteúdo dos segredos do GitHub
firebase_credentials_str = os.getenv("FIREBASE_CREDENTIALS")

# Converter o conteúdo em dicionário
firebase_credentials = {}
for line in firebase_credentials_str.split("\n"):
    if line.strip():
        key, value = line.split("=", 1)
        firebase_credentials[key] = value.strip('"')

# Corrigir as quebras de linha na chave privada
firebase_credentials["FIREBASE_PRIVATE_KEY"] = firebase_credentials["FIREBASE_PRIVATE_KEY"].replace("\\n", "\n")

# Configurar as credenciais do Firebase
firebase_config = {
    "type": firebase_credentials["FIREBASE_TYPE"],
    "project_id": firebase_credentials["FIREBASE_PROJECT_ID"],
    "private_key_id": firebase_credentials["FIREBASE_PRIVATE_KEY_ID"],
    "private_key": firebase_credentials["FIREBASE_PRIVATE_KEY"],
    "client_email": firebase_credentials["FIREBASE_CLIENT_EMAIL"],
    "client_id": firebase_credentials["FIREBASE_CLIENT_ID"],
    "auth_uri": firebase_credentials["FIREBASE_AUTH_URI"],
    "token_uri": firebase_credentials["FIREBASE_TOKEN_URI"],
    "auth_provider_x509_cert_url": firebase_credentials["FIREBASE_AUTH_PROVIDER_X509_CERT_URL"],
    "client_x509_cert_url": firebase_credentials["FIREBASE_CLIENT_X509_CERT_URL"]
}

# Inicializar o Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)
