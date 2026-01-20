import os
import json
from minio import Minio
import pandas as pd
from io import BytesIO

# Configuração MinIO (Pega do ambiente, passado pelo DockerOperator)
MINIO_HOST = os.environ.get("MINIO_HOST", "minio")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minio_access_key")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minio_secret_key")
MINIO_PORT = 9000

LANDING_BUCKET = "landing"
# --- CORREÇÃO 1: BUCKET DE SAÍDA ---
# O script de refinamento (Tarefa 3) lê de 'processing'.
# Portanto, esta tarefa (Tarefa 2) deve escrever em 'processing'.
RAW_BUCKET = "processing" # <- CORRIGIDO (era "raw")
# ----------------------------------
INPUT_FILE = "raw_products.json"
OUTPUT_FILE = "transformed_products.parquet" 

def transform_and_load():
    print("INFO:__main__:Iniciando conexão com MinIO.")
    client = Minio(
        f"{MINIO_HOST}:{MINIO_PORT}",
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    # 1. Leitura do arquivo (GET)
    print(f"INFO:__main__:Lendo arquivo '{INPUT_FILE}' do bucket '{LANDING_BUCKET}'.")
    try:
        response = client.get_object(LANDING_BUCKET, INPUT_FILE)
        data = json.loads(response.read())
        df = pd.DataFrame(data)
    except Exception as e:
        print(f"ERROR:__main__:Erro ao ler ou processar o arquivo: {e}")
        raise
    finally:
        response.close()
        response.release_conn()

    # 2. Transformação (Garantindo tipos e lidando com nulos)
    print("INFO:__main__:Executando transformação: Adicionando timestamp e tratando tipos.")
    
    # --- CORREÇÃO 2: ROBUSTEZ (Null Safety) ---
    # Converte 'price' para numérico, tratando erros (como o 'null')
    # O .astype(float) falha se houver 'None' ou 'null'.
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    # ------------------------------------------
    
    df['ingestion_timestamp'] = pd.Timestamp.now(tz='UTC')

    # 3. Escrita do arquivo transformado (PUT)
    parquet_buffer = BytesIO()
    df.to_parquet(parquet_buffer, index=False)
    parquet_buffer.seek(0)

    print(f"INFO:__main__:Carregando arquivo transformado '{OUTPUT_FILE}' no bucket '{RAW_BUCKET}'.")
    try:
        # Garante que o bucket de destino exista
        if not client.bucket_exists(RAW_BUCKET):
            client.make_bucket(RAW_BUCKET)

        client.put_object(
            RAW_BUCKET,
            OUTPUT_FILE,
            parquet_buffer,
            length=parquet_buffer.getbuffer().nbytes,
            content_type='application/octet-stream'
        )
        print(f"INFO:__main__:Sucesso! Arquivo '{OUTPUT_FILE}' carregado no bucket '{RAW_BUCKET}'.")
    except Exception as e:
        print(f"ERROR:__main__:Erro ao carregar o arquivo no MinIO: {e}")
        raise

if __name__ == "__main__":
    transform_and_load()
