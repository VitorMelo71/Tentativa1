import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from time import sleep
import traceback
from kafka import KafkaProducer
import json
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

BASE_URL = "https://mytkstar.net"
session = requests.Session()

data_form = {
    "txtUserName": os.getenv('TKSTAR_USER'),  # Usuário carregado do .env
    "txtAccountPassword": os.getenv('TKSTAR_PASSWORD'),  # Senha carregada do .env
    "txtImeiNo": "9158080039",
    "txtImeiPassword": "123456",
    "btnLoginImei": "",
    "hidGMT": "-3",
}

def login():
    try:
        get_login = session.get(f"{BASE_URL}/Login.aspx")
        soup = BeautifulSoup(get_login.content, features="html.parser")

        viewstate = soup.select_one("#__VIEWSTATE")
        viewstate_generator = soup.select_one("#__VIEWSTATEGENERATOR")
        event_validation = soup.select_one("#__EVENTVALIDATION")

        if viewstate and viewstate_generator and event_validation:
            data_form["__VIEWSTATE"] = viewstate["value"]
            data_form["__VIEWSTATEGENERATOR"] = viewstate_generator["value"]
            data_form["__EVENTVALIDATION"] = event_validation["value"]
        else:
            print("Erro ao localizar os campos do formulário de login.")
            return False

        payload = urlencode(data_form)
        headers = {"content-type": "application/x-www-form-urlencoded"}
        response = session.post(f"{BASE_URL}/Login.aspx", data=payload, headers=headers)

        if response.status_code == 200:
            print("Login realizado com sucesso.")
            return True
        else:
            print(f"Erro ao realizar login. Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"Erro ao realizar login: {e}")
        print("Stack trace:", traceback.format_exc())
        return False

# Conectar ao MongoDB
def get_database():
    client = MongoClient("mongodb://localhost:27017/")
    return client["bus_tracking"]

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',  # Substitua pelo endereço correto do servidor Kafka
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def enviar_para_kafka(latitude, longitude, status):
    gps_data = {'latitude': latitude, 'longitude': longitude, 'status': status}
    producer.send('gps-coordinates', value=gps_data)
    print("Dados enviados para o Kafka.")

# Salvar a resposta em um arquivo JSON para análise
def save_response_to_file(response_json):
    try:
        with open("Coordenadas_Ônibus.json", "w", encoding="utf-8") as file:
            json.dump(response_json, file, ensure_ascii=False, indent=4)
        print("Resposta salva no arquivo 'Coordenadas_Ônibus.json' para análise.")
    except Exception as e:
        print(f"Erro ao salvar resposta em JSON: {e}")

def extrair_lat_lon(caminho_arquivo, db):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            dados = json.load(arquivo)

        if 'd' in dados and isinstance(dados['d'], str):
            json_str = dados['d']
            json_str = json_str.replace('\"', '"')  
            json_str = json_str.replace('locationID:', '"locationID":')
            json_str = json_str.replace('deviceUtcDate:', '"deviceUtcDate":')
            json_str = json_str.replace('serverUtcDate:', '"serverUtcDate":')
            json_str = json_str.replace('latitude:', '"latitude":')
            json_str = json_str.replace('longitude:', '"longitude":')
            json_str = json_str.replace('baiduLat:', '"baiduLat":')
            json_str = json_str.replace('baiduLng:', '"baiduLng":')
            json_str = json_str.replace('oLat:', '"oLat":')
            json_str = json_str.replace('oLng:', '"oLng":')
            json_str = json_str.replace('speed:', '"speed":')
            json_str = json_str.replace('course:', '"course":')
            json_str = json_str.replace('isStop:', '"isStop":')
            json_str = json_str.replace('dataType:', '"dataType":')
            json_str = json_str.replace('dataContext:', '"dataContext":')
            json_str = json_str.replace('distance:', '"distance":')
            json_str = json_str.replace('stopTimeMinute:', '"stopTimeMinute":')
            json_str = json_str.replace('status:', '"status":')

            try:
                dados_decodificados = json.loads(json_str)
                
                latitude = dados_decodificados.get('latitude')
                longitude = dados_decodificados.get('longitude')
                status = dados_decodificados.get('status')

                if latitude is not None and longitude is not None:
                    print(f"Latitude: {latitude}, Longitude: {longitude}, Status: {status}")
                    save_coordinates_to_mongodb(db, latitude, longitude, status)
                else:
                    print("Latitude ou longitude não encontrados nos dados decodificados.")
            
            except json.JSONDecodeError:
                print("Erro ao decodificar a string JSON interna.")
        else:
            print("Chave 'd' não encontrada ou não é uma string.")
    
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
    except json.JSONDecodeError:
        print("Erro ao decodificar o conteúdo JSON. Verifique o formato do arquivo.")
    except Exception as e:
        print(f"Erro inesperado: {e}")

# Função principal
def app():
    db = get_database()  # Conecta ao MongoDB
    if not login():
        print("Falha no login. O programa será encerrado.")
        return

    while True:
        try:
            result_locale = session.post(
                f"{BASE_URL}/Ajax/DevicesAjax.asmx/GetTracking",
                data="{DeviceID:1719220,TimeZone:'-3:00'}",
                headers={"content-type": "application/json"},
            )

            if result_locale.status_code != 200:
                print(f"Erro na solicitação de rastreamento: {result_locale.status_code}")
                continue

            print("Resposta completa da API:", result_locale.text[:1000])
            
            try:
                data_result_locale = result_locale.json()
            except ValueError:
                print("A resposta não está no formato JSON.")
                continue

            tracking_info = data_result_locale.get("d")
            if not tracking_info:
                print("Resposta vazia. Tentando realizar login novamente...")
                login()
                continue

            if isinstance(tracking_info, str):
                print("Analisando a string 'd':", tracking_info[:500])
            else:
                print("Formato inesperado de 'd':", type(tracking_info), tracking_info)

            save_response_to_file(data_result_locale)
            extrair_lat_lon('Coordenadas_Ônibus.json', db)

        except requests.exceptions.RequestException as e:
            print(f"Erro de rede: {e}")
            sleep(10)
            login()
            continue
        except Exception as e:
            print(f"Erro inesperado: {e}")
            print("Stack trace:", traceback.format_exc())
            break

        sleep(5.0)

if __name__ == "__main__":
    app()