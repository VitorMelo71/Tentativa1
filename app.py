import streamlit as st
import os
import json
import firebase_admin
from firebase_admin import credentials
import folium
from streamlit_folium import st_folium
from streamlit.runtime.scriptrunner import RerunException
from streamlit.runtime.state.session_state import SessionState

# Função para inicializar Firebase
def initialize_firebase():
    # Carregar o conteúdo das credenciais do Firebase
    firebase_credentials_str = os.getenv("FIREBASE_CREDENTIALS")
    
    if firebase_credentials_str is None:
        st.error("O segredo FIREBASE_CREDENTIALS não está carregado.")
    else:
        try:
            # Carregar as credenciais como JSON
            firebase_credentials = json.loads(firebase_credentials_str)
            st.write("Credenciais do Firebase carregadas com sucesso.")
            
            # Inicializar o Firebase com as credenciais carregadas em formato de dicionário
            cred = credentials.Certificate(firebase_credentials)
            firebase_admin.initialize_app(cred)
        except json.JSONDecodeError as e:
            st.error(f"Erro ao decodificar as credenciais JSON: {e}")
        except Exception as e:
            st.error(f"Erro inesperado: {e}")

# Função para criar o mapa
def criar_mapa(lat, lon, zoom):
    mapa = folium.Map(location=[lat, lon], zoom_start=zoom, control_scale=True)
    folium.Marker([lat, lon], tooltip="Você está aqui!").add_to(mapa)
    return mapa

# Inicializar o Firebase
if "firebase_initialized" not in st.session_state:
    initialize_firebase()
    st.session_state.firebase_initialized = True

# Configuração inicial do mapa
if 'lat' not in st.session_state:
    st.session_state.lat = -1.2921  # Latitude padrão (exemplo: Nairobi)
if 'lon' not in st.session_state:
    st.session_state.lon = 36.8219  # Longitude padrão
if 'zoom' not in st.session_state:
    st.session_state.zoom = 10  # Nível de zoom padrão

# Mostrar o mapa
mapa = criar_mapa(st.session_state.lat, st.session_state.lon, st.session_state.zoom)
mapa_data = st_folium(mapa, width=350, height=500)

# Verificar se o usuário movimentou o mapa e atualizar as coordenadas e zoom
if mapa_data and mapa_data['last_center']:
    st.session_state.lat = mapa_data['last_center'][0]
    st.session_state.lon = mapa_data['last_center'][1]
    st.session_state.zoom = mapa_data['last_zoom']
