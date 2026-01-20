#!/bin/bash

# --- CONFIGURAÇÃO DE TESTE ---
# 1. Altere o conteúdo da variável JSON_DATA para o seu novo teste.

# !!!!!!! ATENÇÃO: VERIFIQUE SE ESTE CAMINHO ABSOLUTO ESTÁ CORRETO !!!!!!!
HOST_SCRIPTS_PATH="/home/lion92185/data-engineer-junior-project/scripts" 

# NOME CORRETO DO CONTÊINER (com sublinhado _)
AIRFLOW_WEBSERVER_CONTAINER="data-engineer-junior-project_airflow-webserver_1" 

TEST_FILE_NAME="temp_test_data.json"
DAG_ID="ingestion_to_landing"

# JSON DATA DE TESTE (com valor nulo para o Portable Speaker)
JSON_DATA='
[
    {
        "id": 201,
        "product_name": "Mechanical Keyboard",
        "price": 150.00,
        "category": "Electronics",
        "stock": 75
    },
    {
        "id": 202,
        "product_name": "Aged Cheddar Cheese",
        "price": 25.50,
        "category": "Food",
        "stock": 150
    },
    {
        "id": 203,
        "product_name": "T-shirt Cotton Blend",
        "price": 35.00,
        "category": "Apparel",
        "stock": 500
    },
    {
        "id": 204,
        "product_name": "Portable Speaker",
        "price": null,
        "category": "Electronics",
        "stock": 20
    }
]
'
# -----------------------------


echo "==========================================================="
echo " PASSO 1/3: Criando arquivo temporário no host: ${TEST_FILE_NAME}"
echo "==========================================================="
# Cria o arquivo JSON no host
echo "${JSON_DATA}" > "${TEST_FILE_NAME}"


echo ""
echo "==========================================================="
echo " PASSO 2/3: Substituindo o 'raw_products.json' no MinIO"
echo "==========================================================="
# Monta o caminho ABSOLUTO para o script de upload
docker run --rm \
  --net data-engineer-junior-project_default \
  -v "${HOST_SCRIPTS_PATH}:/opt/airflow/scripts:ro" \
  -v "$(pwd)/${TEST_FILE_NAME}:/tmp/new_data.json" \
  -e LOCAL_FILE_PATH="/tmp/new_data.json" \
  -e MINIO_HOST="minio" \
  -e MINIO_ACCESS_KEY="minio_access_key" \
  -e MINIO_SECRET_KEY="minio_secret_key" \
  custom-airflow:2.7.2 \
  python /opt/airflow/scripts/upload_override.py
  

echo ""
echo "==========================================================="
echo " PASSO 3/3: Disparando a DAG '${DAG_ID}' no Airflow para reprocessamento"
echo "==========================================================="
# Executa o comando 'trigger' na DAG
docker exec ${AIRFLOW_WEBSERVER_CONTAINER} airflow dags trigger ${DAG_ID}

echo ""
echo "==========================================================="
echo " TESTE CONCLUÍDO. VERIFIQUE O AIRFLOW UI E CONSULTE O DATA MART."
echo "==========================================================="

# Limpa o arquivo temporário
rm "${TEST_FILE_NAME}"
