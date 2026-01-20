# scripts/extract_data.py

import os
import json
import logging
from minio import Minio

# Configurações de Log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configurações MinIO ---
# Lidas das variáveis de ambiente do Docker Compose, garantindo que o DockerOperator as use.
MINIO_HOST = os.environ.get("MINIO_HOST", "minio")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minio_access_key")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minio_secret_key")
MINIO_PORT = 9000

# Dados simulados (RAW data)
SIMULATED_DATA = [
    {"id": 101, "product_name": "Laptop Pro X", "price": 1800.00, "category": "Electronics", "stock": 50},
    {"id": 102, "product_name": "Organic Coffee", "price": 15.99, "category": "Food", "stock": 300},
    {"id": 103, "product_name": "Running Shoes", "price": 99.50, "category": "Apparel", "stock": 120},
]

def extract_and_save_to_minio():
    """
    Simula a extração de dados e os carrega no bucket 'landing' do MinIO.
    """
    logger.info(f"Iniciando a conexão com o MinIO em: {MINIO_HOST}:{MINIO_PORT}")
    
    # 1. Conectar ao cliente MinIO
    client = Minio(
        f"{MINIO_HOST}:{MINIO_PORT}",
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False # Usar False para conexões HTTP
    )

    # Nome do bucket de destino e nome do arquivo no Data Lake
    BUCKET_NAME = "landing"
    OBJECT_NAME = "raw_products.json"
    
    # 2. Criar o arquivo localmente em /tmp (local temporário dentro do container)
    file_path = "/tmp/data.json"
    with open(file_path, 'w') as f:
        json.dump(SIMULATED_DATA, f, indent=4)
    logger.info(f"Dados simulados escritos temporariamente em {file_path}")

    # 3. Upload para o MinIO
    try:
        client.fput_object(
            bucket_name=BUCKET_NAME,
            object_name=OBJECT_NAME,
            file_path=file_path,
            content_type='application/json'
        )
        logger.info(f"Sucesso! Arquivo '{OBJECT_NAME}' carregado no bucket '{BUCKET_NAME}'.")
        
    except Exception as e:
        logger.error(f"ERRO ao carregar para o MinIO: {e}")
        # É crucial levantar o erro para o Airflow marcar a tarefa como falha
        raise 

if __name__ == "__main__":
    extract_and_save_to_minio()
