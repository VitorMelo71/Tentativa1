import streamlit as st
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

# Interface Streamlit
st.title("Rastreamento de Ônibus em Tempo Real")

# Pega as últimas coordenadas
latitude, longitude = get_latest_coordinates()

# Exibe os dados na interface
st.write(f"Última Localização: Latitude {latitude}, Longitude {longitude}")
