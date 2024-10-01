import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import tempfile
import folium
from streamlit_folium import st_folium
import time

# Carregar as credenciais do Firebase a partir do Secrets do Streamlit
firebase_credentials = {
    "type": "service_account",
    "project_id": "banco-gps",
    "private_key_id": "bb80c06604b6b890d70b6630119c1b8674f57b81",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCb8p6b+eWEA2pv\n3pDghEftg5r+TRR57YPX5UoaMq+kAPwwVDfR+G5pK13p7zjUI5QthkzdoAYycAQ1\nVHE0STyT64nPeJ6ckQ5I2wdy10Ue2/vMMSegIj3WEDytN1YCHGllLRray1oL8PWf\n3xM/qFe+D2F8woJX8SkP591DbHyVkjj8ZIVontRLWOcO9q7gDjkHh0A/XY91jP8F\n+DrFV9aWDw2wGfmYP1kdmib311ETPV+TqPcMdDsXx2dlp+/6zgDIMKcFHzSrnnmT\nFNcUpGEoIUTYZaauY4LgJ4m4zlzCvCR8u0e0mK1780FgERipWUhjCasAAjsfwHa8\ny3c6Y9RHAgMBAAECggEAFxSP8+7G0MR+psLud0QsrxLoyBVZX/hOqI/XaUwyIZhB\nutdkEY/uq2MPObW9l+wSHLDBRJXQBPv+K3RtcrsaG5xjH5EvDGYNkqvUDOOeZ8RQ\nHnbx8enPdBSgHlTPxm01DhPgYxxwnc7SU5B89VFxdwAowgG5r9FR7fg3j6iJQcuQ\nn5HY5lZup67ZKFX6JPrlt84vBy/Md/xV/biKjLV+4hVBBedO8nef1ge2gH+jI2PT\ny8CJEqWCtjMaBw8MpgBYo+QiZSQzP+eQ1DJe3thAgVFXA0Qyjr9Uu8sfG1yRxmyL\nLXKuHTUlC11rsEvna1qnl+JO2b3VWVrrQHwGhjpf7QKBgQDU09B1m2qtXgQmZF8Y\nbfKklZ6GX6wbXDEY1qPgNOrhs1nTXampfex8q6o7LQc2ApIgve0cz8qG9EKo647t\n9pMOQPL5YsCO4+zleptl4DtCZbEKatcE9NOC1Nyjp3XLFZ0eNIWzJWpHi8EF3w9h\n6LucSZVMsqIroLlOD/jl2HmpBQKBgQC7lQdIGz1IxfBzJRr8fu8F51JKKxpV7Jn2\nktFHRwMQose6AfvYEqeTMznSKLCF0xTdo+G0b+3oPxPvE1xHSK5SNdL5/tXhn6kB\n/VZFiBmWpf2e4JlkPllksOMEnkRw0ScO/fS+dhnYMZzLEEQc/hVhLnqyT2p0/8eZ\n+FbPc8/Z2wKBgQCv0PuY7HdIGS7ceHaGu+2DQYbgAxEu2Q5GMqrWgWC4a219Sxbp\nyfkfVMEgeaZHXABTxBKpho8MxaR7330H4HbDg6w1kPr6EBiXyp2tn3vU8iU7Md/H\nXGmO30IWgDSzPHu7hDAfOn199VnT+929SIIULkWEQt3tpKzwbAl190sp8QKBgFlV\nSOl7J31/3tpHYom7PcP2/UabLmibTFuUYhxq4jfK/glEppapk6rTq4a9oAurkfVX\n9caDw65mU+z4sGq2X2aBgZ9TULKp4cgzySFGBsGq/ZTra8HEu7frUcJCSV/dC5fl\nM+h8wCQoxH4kmfugubfVddNzZMShh4J5NYaIpgUfAoGAI7ToIhEyow8LAFJpOX4u\n54orYVtCB98qRRZDZ0vJM/w3MYoGj5pqJ3R1d/h2dFGW9WYSg234d0YwvZbW6c8S\nTU5TaRuZlbaShylARxvZt9AjRQ+YLKROxbYjUjNXbNlB9W9LgzlDef+RreYRnBFw\nSRD3ng8WviKShg/hj9W2JHI=\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-x0vc4@banco-gps.iam.gserviceaccount.com",
    "client_id": "103774825751829582460",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-x0vc4%40banco-gps.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# Corrigir quebras de linha na chave privada
firebase_credentials["private_key"] = firebase_credentials["private_key"].replace("\\n", "\n")

# Criar um arquivo temporário para armazenar as credenciais do Firebase
with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
    json.dump(firebase_credentials, temp_file)
    temp_file.flush()

    # Inicializar Firebase com o caminho do arquivo temporário de credenciais
    if not firebase_admin._apps:  # Verificar se o Firebase já foi inicializado
        cred = credentials.Certificate(temp_file.name)
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

# Função para exibir o mapa no Streamlit
def exibir_mapa(latitude, longitude):
    mapa = folium.Map(location=[latitude, longitude], zoom_start=15)
    folium.Marker([latitude, longitude], tooltip="Ônibus").add_to(mapa)
    st_folium(mapa, width=725)

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
