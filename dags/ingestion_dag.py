from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime, timedelta
# IMPORTAÇÃO ESSENCIAL para a montagem de volumes robusta
from docker.types import Mount 

# Defina o nome da imagem Docker que você CONSTRUIU com o docker-compose build
DOCKER_IMAGE = "custom-airflow:2.7.2"

# O nome da rede do seu ambiente Docker Compose
NETWORK_NAME = "data-engineer-junior-project_default" 

# CAMINHO ABSOLUTO CORRIGIDO DO HOST - Usado na classe Mount
# MANTENHA O CAMINHO ABSOLUTO DO SEU AMBIENTE:
HOST_SCRIPTS_PATH = "/home/lion92185/data-engineer-junior-project/scripts"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'ingestion_to_landing',
    default_args=default_args,
    description='Pipeline ETL completo: Landing, Raw e Curated Zones.',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['datalake', 'minio', 'etl'],
) as dag:
    
    # 1. TAREFA: Extração e Carga para Landing (Extract & Load)
    extract_and_load_task = DockerOperator(
        task_id='extract_and_load_to_minio',
        image=DOCKER_IMAGE,
        command='python /opt/airflow/scripts/extract_data.py',

        user='root', 
        mounts=[
            Mount(
                source=HOST_SCRIPTS_PATH,
                target='/opt/airflow/scripts',
                type='bind',
                read_only=True
            )
        ],
        api_version='auto',
        docker_url='unix:///var/run/docker.sock',
        mount_tmp_dir=False, 

        environment={
            "MINIO_HOST": "minio",
            "MINIO_ACCESS_KEY": "minio_access_key",
            "MINIO_SECRET_KEY": "minio_secret_key",
        },

        network_mode=NETWORK_NAME, 
        do_xcom_push=False,
        auto_remove=True,
    )
    
    # 2. TAREFA: Transformação e Carga para Raw (Transform)
    transform_data_task = DockerOperator(
        task_id='transform_data_to_raw',
        image=DOCKER_IMAGE,
        command='python /opt/airflow/scripts/transformation.py',

        user='root',
        mounts=[
            Mount(
                source=HOST_SCRIPTS_PATH,
                target='/opt/airflow/scripts',
                type='bind',
                read_only=True
            )
        ],
        api_version='auto',
        docker_url='unix:///var/run/docker.sock',
        mount_tmp_dir=False,

        environment={
            "MINIO_HOST": "minio",
            "MINIO_ACCESS_KEY": "minio_access_key",
            "MINIO_SECRET_KEY": "minio_secret_key",
        },
        network_mode=NETWORK_NAME,
        do_xcom_push=False,
        auto_remove=True,
    )

    # 3. TAREFA: Refinamento e Carga para Curated (Modelagem/Refine)
    refine_data_task = DockerOperator(
        task_id='refine_data_to_curated',
        image=DOCKER_IMAGE,
        # O SCRIPT CHAMA A FUNÇÃO DE REFINAMENTO
        command='python /opt/airflow/scripts/refine_data.py',

        user='root',
        mounts=[
            Mount(
                source=HOST_SCRIPTS_PATH,
                target='/opt/airflow/scripts',
                type='bind',
                read_only=True
            )
        ],
        api_version='auto',
        docker_url='unix:///var/run/docker.sock',
        mount_tmp_dir=False,

        environment={
            "MINIO_HOST": "minio",
            "MINIO_ACCESS_KEY": "minio_access_key",
            "MINIO_SECRET_KEY": "minio_secret_key",
        },
        network_mode=NETWORK_NAME,
        do_xcom_push=False,
        auto_remove=True,
    )

    # 4. ORDEM DA DAG: O pipeline completo (E -> T -> L)
    extract_and_load_task >> transform_data_task >> refine_data_task
