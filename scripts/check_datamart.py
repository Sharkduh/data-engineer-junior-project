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

CURATED_BUCKET = "curated"
FINAL_FILE = "dim_products.parquet"

def check_datamart():
    print("-------------------------------------------------")
    print("INFO:__main__:Simulando a Consulta ao Data Mart...")

    client = Minio(
        f"{MINIO_HOST}:{MINIO_PORT}",
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )
    
    # 1. Checa se o arquivo existe
    try:
        client.stat_object(CURATED_BUCKET, FINAL_FILE)
        print(f"INFO:__main__:Sucesso! O arquivo '{FINAL_FILE}' existe no bucket '{CURATED_BUCKET}'.")
    except S3Error as e:
        if e.code == 'NoSuchKey':
            print(f"ERROR:__main__:Arquivo '{FINAL_FILE}' não encontrado no Data Mart. Pipeline não finalizou.")
            return
        else:
            print(f"ERROR:__main__:Erro ao checar o arquivo: {e}")
            raise
    
    # 2. Leitura do Parquet
    try:
        response = client.get_object(CURATED_BUCKET, FINAL_FILE)
        
        # Lê o Parquet diretamente para um DataFrame do Pandas
        df = pd.read_parquet(BytesIO(response.read()))
        
        response.close()
        response.release_conn()
        
        print(f"INFO:__main__:Dados lidos do arquivo '{FINAL_FILE}'.")

    except S3Error as e:
        print(f"ERROR:__main__:Erro de leitura no MinIO: {e}")
        return
    except Exception as e:
        print(f"ERROR:__main__:Erro ao processar o Parquet: {e}")
        return

    # 3. Exibição do Resultado
    print("\n--- Conteúdo do Data Mart (Dim Products) ---")
    print(df.to_string(index=False)) # to_string é melhor para display em terminais
    print("-------------------------------------------------")

if __name__ == "__main__":
    check_datamart()
