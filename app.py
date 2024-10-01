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
    # (mesmo conteúdo das credenciais)
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

# Função para buscar a última localização do Firestore
def buscar_localizacao():
    doc_ref = db.collection(u'CoordenadasGPS').document(u'veiculo')
    doc = doc_ref.get()
    if doc.exists():
        data = doc.to_dict()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        status = data.get('status')
        return float(latitude), float(longitude), status
    else:
        return None, None, None

# Função para exibir o mapa no Streamlit com o ícone do ônibus arredondado
def exibir_mapa(latitude, longitude, last_position=None):
    # Se o usuário moveu o mapa, usamos essa última posição
    if last_position:
        mapa = folium.Map(location=last_position, zoom_start=15)
    else:
        # Caso contrário, centralizamos no veículo
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
    
    # Dimensões aproximadas de um iPhone 11 (828 x 1792 pixels)
    map_data = st_folium(mapa, width=375, height=812, returned_objects=["last_center"])

    # Retornar a última posição visualizada pelo usuário, se houver
    return map_data.get("last_center", [latitude, longitude])

st.title('Circular UFPA')

# Inicializar variável para guardar última posição
last_position = None

# Atualizar localização a cada 10 segundos
while True:
    latitude, longitude, status = buscar_localizacao()
    if latitude is not None and longitude is not None:
        st.write(f"Status: {status}")
        # Exibir o mapa e obter a última posição visualizada pelo usuário
        last_position = exibir_mapa(latitude, longitude, last_position)
    else:
        st.write("Aguardando atualização de localização...")

    time.sleep(10)  # Atualizar a cada 10 segundos
