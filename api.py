import streamlit as st
import folium
from kafka import KafkaConsumer
import json

# Configurações do Kafka Consumer
consumer = KafkaConsumer(
    'gps-coordinates',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Função para consumir as últimas coordenadas do Kafka
def get_latest_coordinates():
    for message in consumer:
        gps_data = message.value
        return gps_data['latitude'], gps_data['longitude']

# Interface Streamlit com Mapa
st.title("Rastreamento de Ônibus em Tempo Real")

latitude, longitude = get_latest_coordinates()

if latitude and longitude:
    # Cria o mapa com as coordenadas mais recentes
    folium_map = folium.Map(location=[latitude, longitude], zoom_start=15)
    folium.Marker([latitude, longitude], popup="Localização do Veículo").add_to(folium_map)

    # Exibe o mapa no Streamlit
    st.write(folium_map)
else:
    st.write("Não foram encontradas coordenadas no Kafka.")
