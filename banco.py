import boto3

# Conectar ao DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Selecionar a tabela
table = dynamodb.Table('CoordenadasGPS')

# Função para enviar dados ao DynamoDB
def enviar_para_dynamodb(latitude, longitude, status):
    response = table.put_item(
        Item={
            'Latitude': latitude,
            'Longitude': longitude,
            'Status': status
        }
    )
    print(f"Dados enviados ao DynamoDB: {response}")

# Modifique o código para armazenar os dados no DynamoDB ao invés de apenas Kafka
