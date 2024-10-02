import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import tempfile

# Interface para upload do arquivo JSON no Streamlit
uploaded_file = st.file_uploader("Upload seu arquivo JSON do Firebase", type="json")

if uploaded_file is not None:
    # Salvar o arquivo temporariamente
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        json_file_path = tmp_file.name

    # Inicializar Firebase com o arquivo JSON carregado
    if not firebase_admin._apps:
        cred = credentials.Certificate(json_file_path)
        firebase_admin.initialize_app(cred)

    # Inicializar o Firestore
    db = firestore.client()

    # Exemplo de uma consulta ao Firestore
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

    # Use a função para buscar e exibir a localização
    latitude, longitude, status = buscar_localizacao()
    if latitude is not None and longitude is not None:
        st.write(f"Localização: {latitude}, {longitude} - Status: {status}")
    else:
        st.write("Aguardando atualização de localização...")
