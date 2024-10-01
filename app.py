import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import tempfile
import folium
from streamlit_folium import st_folium
import time

# Credenciais Firebase atualizadas
firebase_credentials = {
    "type": "service_account",
    "project_id": "banco-gps",
    "private_key_id": "6929102941a72fc9caed116f0f4c1065e5447b0b",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDF8rPDjqWjUhSj\nIIyrhrJ1F/ywqoM4FDekVJCLpCt/gwDswgKnY12Z8YCZrqRBu/eHBTKhPGvtWbzi\nkopcbPrUvI9pI0gyhbBsD/GNqGDGm6nM21pcVHowf7UnZv+0VDkLt7h0dcAT4EFM\nEzX3V9e/35uOXeSX6aseQMLdswQn1OWix+DdM06CtCGiTUwk4ATBU06/H9Ohl5B4\n6lhhx8jI5YB2wi1Yy3aIzX/hUCglcgmnIYauhqo4RMYheJRcUEIWZtXkFFtVrQzM\nPnHMHlyTdoinBFlv8MFUJHJWoLvuSs8b6gVuWYGcTOdPq3hx4TJENK5hjr00cObk\nuXaeOTXjAgMBAAECggEASO123zhhu/8UjVkDmnogq1UwCqJ3f6SrL0bcjiXoxKyu\nHYwI0ESiioHYIEagS3uF4V+/3HlXRfXGyi60/QJFkzT5HQIbqkloyxdApjD/noxh\nDZFPBC83aUDTq/WdhYF2FuQT+AwdvPTk+bMmMb9SRGWMePIMsw8qtRWk9WrrwARf\n5QDTgvvYZMQ9T/yjHHvURjor8cnljFSQ2xlLX4oypfLQQv2tus9rCBpEBkbuUvjr\njEN2EA2HfuJy9tM754IYiK/fILOm29Ym+3O+dVG+GDKY9AEDnTqXQm5zu4UJTFg8\nwPVczWbNOaFePibkTKFaQZONXUlUKP9EoF433OkXgQKBgQD5yDoFUyFOhMUYnx9l\n9X5uB30thiv6qg7GWqJVd3LsxpX+kSf7deCH6NYuschO1hso3jDbTMQF9YAo8/9z\n3PnICpnvBlfh7DBubua7zI9/PTXYlYm5fb/rJW+MOD+x0QeAyWE2EI2CnRxqska3\nWAbwZy7Q/lEUXIE7iXaEcy1CowKBgQDK4Ce/vcaEGA1F4+Q7L1bkr7IUPsvXHqKz\nSKiIVGpGUeDVzCKvaoYEps02e4fXrZrFi3y/Z54GZ5+POMCR+CIhl0CRUXdOuIS9\n/F0LhKv0KjviGHohaXUUmYqlUNmVHv7+BtoMvJ7E8WZUAwzKTyJmDQMpaPrpUIPg\nanIzCJazwQKBgDT6LrQqaYoJxvPt6+7oHqSfmgEpz/IeV3vihUOzTgDCLdYMW3qO\nCc1JqQPGWUG/T4tfdOVOZtUMuN32wluEpsWy2etEYSddvPfvNajnPhgyl1UUgl2B\nOk9ZZUtMMtY4C2tZSvD4mcr2H6zRmwYP+YjLmbZh+jhjVlWWVjjJZPQZAoGASMCl\nwH7/x7MQX3XgDNFnKc9P3y69zsEvu3dc6LbM/bazGDiCX8GlmdlvUhBuoIujKyBg\ndgtkggt7DtNdS3teUgl5oCNE07gb8j2j6FOFjqPuoaABfCXjVKXTMIGT5YQeEV7H\npzWlAh9HgO0vEwXZ4hrcfWcmQ7EZ+cpydZao5IECgYAVElQIOd/LIABXj31l9S7C\nmEfxGKWi8iCYCoWT9tlc6CiYvwCRNoWs/kkxqRKcZjWO8wlWuCgKlZ8e+PTrk5BD\nnDHVCgTrubJ5d5lqHtnoDBHyNQqcS2tfrBy7Rukqmlhf811dctKRwssagrWQMxaE\nvmUBlP1nuzGrOcZJ5UsOmA==\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-x0vc4@banco-gps.iam.gserviceaccount.com",
    "client_id": "103774825751829582460",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-x0vc4@banco-gps.iam.gserviceaccount.com",
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

# Função para exibir o mapa no Streamlit com o ícone do ônibus
def exibir_mapa(latitude, longitude):
    mapa = folium.Map(location=[latitude, longitude], zoom_start=15)

    # Adicionar o ícone personalizado (imagem do ônibus redonda)
    icon_bus = folium.CustomIcon("https://raw.githubusercontent.com/VitorMelo71/Tentativa1/main/sa.jpg", icon_size=(50, 50))

    folium.Marker([latitude, longitude], tooltip="Ônibus", icon=icon_bus).add_to(mapa)
    
    # Renderizar o mapa no Streamlit
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
