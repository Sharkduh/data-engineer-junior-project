import os
import requests
from minio import Minio

# Variáveis de Conexão com o MinIO (Data Lake)
# NOTA: O Airflow usa as variáveis de ambiente definidas no docker-compose
MINIO_HOST = os.getenv("MINIO_HOST", "minio")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio_access_key")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio_secret_key")
MINIO_URL = f"{MINIO_HOST}:9001"

# URL de Conexão com o Airflow Webserver (para criar a conexão)
AIRFLOW_URL = "http://localhost:8080" # Acessível DENTRO do container
AIRFLOW_API_USER = "airflow"
AIRFLOW_API_PASSWORD = "airflow"

# Buckets (Data Lakes) a serem criados
BUCKETS = [
    "landing",    # Camada RAW (Dados brutos)
    "processing", # Camada STAGING (Dados limpos)
    "curated"     # Camada CONSUMO (Dados modelados/prontos)
]

def create_minio_buckets():
    """Conecta ao MinIO e garante que os buckets existam."""
    print(f"-> Conectando ao MinIO em: {MINIO_URL}")
    
    # Inicializa o cliente MinIO
    # A porta 9001 é usada para a API do S3
    client = Minio(
        MINIO_URL,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    for bucket_name in BUCKETS:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"   Bucket '{bucket_name}' criado com sucesso.")
        else:
            print(f"   Bucket '{bucket_name}' já existe. Ignorando.")

def create_airflow_connection():
    """Cria a conexão 'minio_s3_conn' no Airflow via API."""
    print("-> Criando/Atualizando conexão 'minio_s3_conn' no Airflow.")
    
    connection_id = "minio_s3_conn"
    connection_payload = {
        "connection_id": connection_id,
        "conn_type": "s3",
        "host": f"http://{MINIO_HOST}:9001",
        "login": MINIO_ACCESS_KEY,
        "password": MINIO_SECRET_KEY,
        # O extra é crucial para configurar o MinIO como endpoint S3
        "extra": '{"aws_access_key_id": "' + MINIO_ACCESS_KEY + '", "aws_secret_access_key": "' + MINIO_SECRET_KEY + '", "endpoint_url": "http://minio:9001", "s3_conn_id": "' + connection_id + '", "disable_ssl": "true", "verify": "false"}'
    }

    api_url = f"{AIRFLOW_URL}/api/v1/connections/{connection_id}"
    
    try:
        # Tenta criar a conexão (POST)
        response = requests.post(
            f"{AIRFLOW_URL}/api/v1/connections",
            json=connection_payload,
            auth=(AIRFLOW_API_USER, AIRFLOW_API_PASSWORD)
        )
        if response.status_code == 200:
            print(f"   Conexão '{connection_id}' criada com sucesso.")
            return

        # Se falhou com 409 (Conflict), tenta atualizar (PATCH)
        elif response.status_code == 409:
            print(f"   Conexão '{connection_id}' já existe. Tentando atualizar.")
            response = requests.patch(
                api_url,
                json=connection_payload,
                auth=(AIRFLOW_API_USER, AIRFLOW_API_PASSWORD)
            )
            if response.status_code == 200:
                print(f"   Conexão '{connection_id}' atualizada com sucesso.")
                return
        
        response.raise_for_status()
    
    except requests.exceptions.HTTPError as e:
        print(f"   Erro ao criar/atualizar conexão: {e.response.text}")
    except requests.exceptions.ConnectionError:
        print(f"   ERRO: Não foi possível conectar ao Airflow API em {AIRFLOW_URL}. Verifique se o Webserver está rodando e acessível.")

if __name__ == "__main__":
    create_minio_buckets()
    create_airflow_connection()
