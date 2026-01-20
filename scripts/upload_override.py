import os
from minio import Minio
from minio.error import S3Error

# Configuração MinIO
MINIO_HOST = os.environ.get("MINIO_HOST", "minio")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minio_access_key")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minio_secret_key")
MINIO_PORT = 9000

# Arquivo que será sobrescrito no MinIO
TARGET_BUCKET = "landing"
TARGET_OBJECT = "raw_products.json"

# Arquivo que será LIDO da sua máquina (o novo dado de teste)
LOCAL_FILE_PATH = os.environ.get("LOCAL_FILE_PATH") 

def override_minio_file():
    print("-------------------------------------------------")
    print(f"INFO:__main__:Iniciando upload de '{LOCAL_FILE_PATH}' para MinIO...")
    
    if not LOCAL_FILE_PATH or not os.path.exists(LOCAL_FILE_PATH):
        print(f"ERROR:__main__:Caminho do arquivo local não encontrado ou inválido: {LOCAL_FILE_PATH}")
        return

    client = Minio(
        f"{MINIO_HOST}:{MINIO_PORT}",
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    try:
        # O fput_object sobrescreve o arquivo existente se o nome for o mesmo
        client.fput_object(
            TARGET_BUCKET,
            TARGET_OBJECT,
            LOCAL_FILE_PATH,
            content_type='application/json'
        )
        print(f"INFO:__main__:Sucesso! '{TARGET_OBJECT}' foi sobrescrito no bucket '{TARGET_BUCKET}'.")
    except S3Error as e:
        print(f"ERROR:__main__:Erro no MinIO: {e}")
    except Exception as e:
        print(f"ERROR:__main__:Erro geral: {e}")

if __name__ == "__main__":
    override_minio_file()
