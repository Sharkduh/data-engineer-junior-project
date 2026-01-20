import os
from minio import Minio
import pandas as pd
from io import BytesIO
from minio.error import S3Error

# --- CONFIGURAÇÃO MINIO ---
MINIO_HOST = os.environ.get("MINIO_HOST", "minio")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minio_access_key")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minio_secret_key")
MINIO_PORT = 9000

# --- CORREÇÃO DE BUG ---
# A Tarefa 2 (transform) salva em 'processing'.
# A Tarefa 3 (refine) deve ler de 'processing'.
INPUT_BUCKET = "processing" # <- CORRIGIDO (era "raw")
# -----------------------
INPUT_FILE = "transformed_products.parquet"
CURATED_BUCKET = "curated"
OUTPUT_FILE = "dim_products.parquet" 

def refine_and_load():
    print("INFO:__main__:Iniciando conexão com MinIO.")
    client = Minio(
        f"{MINIO_HOST}:{MINIO_PORT}",
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    # 1. Leitura do arquivo (GET) do bucket 'processing'
    print(f"INFO:__main__:Lendo arquivo '{INPUT_FILE}' do bucket '{INPUT_BUCKET}'.")
    try:
        response = client.get_object(INPUT_BUCKET, INPUT_FILE)
        
        # Leitura do Parquet diretamente na memória
        df = pd.read_parquet(BytesIO(response.read()))
    except Exception as e:
        print(f"ERROR:__main__:Erro ao ler o arquivo Parquet: {e}")
        print(f"INFO:__main__:Verifique se o bucket '{INPUT_BUCKET}' contém o arquivo.")
        raise
    finally:
        response.close()
        response.release_conn()

    # 2. Modelagem (Refinamento): Seleciona colunas e trata nulos
    print("INFO:__main__:Executando modelagem: Seleção e refinamento de colunas.")
    
    # Garante que 'price' é numérico e lida com o 'null' do teste
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    
    df_curated = df[[
        'id', 
        'product_name', 
        'price', 
        'category'
    ]].copy()
    
    df_curated.rename(columns={
        'id': 'product_key',
        'product_name': 'name',
        'price': 'unit_price'
    }, inplace=True)


    # 3. Escrita do arquivo modelado (PUT)
    parquet_buffer = BytesIO()
    df_curated.to_parquet(parquet_buffer, index=False)
    parquet_buffer.seek(0)
    
    print(f"INFO:__main__:Carregando arquivo modelado '{OUTPUT_FILE}' no bucket '{CURATED_BUCKET}'.")
    try:
        if not client.bucket_exists(CURATED_BUCKET):
            client.make_bucket(CURATED_BUCKET)

        client.put_object(
            CURATED_BUCKET,
            OUTPUT_FILE,
            parquet_buffer,
            length=parquet_buffer.getbuffer().nbytes,
            content_type='application/octet-stream'
        )
        print(f"INFO:__main__:Sucesso! Arquivo '{OUTPUT_FILE}' carregado no bucket '{CURATED_BUCKET}'.")
    except Exception as e:
        print(f"ERROR:__main__:Erro ao carregar o arquivo no MinIO: {e}")
        raise

if __name__ == "__main__":
    refine_and_load()
