# ARGS é o nome da variável passada do docker-compose
ARG AIRFLOW_BASE_IMAGE

# O Airflow inicia a partir da imagem base definida
FROM ${AIRFLOW_BASE_IMAGE}

# --- CRITICAL FIX: Mapeamento do Docker Group ID (GID) ---
# O GID do seu grupo 'docker' no Host é 1002.
ARG DOCKER_GID=1002

# 1. Temporariamente, mude para o usuário root para garantir que a modificação de grupo funcione
USER root
# Cria um grupo chamado 'docker' com o GID do host (1002) e adiciona o usuário 'airflow' a ele.
# Isso resolve o PermissionError (Errno 13).
RUN groupadd -g ${DOCKER_GID} docker && \
    usermod -aG docker airflow

# 2. Volte para o usuário 'airflow' (o usuário padrão da imagem Airflow para segurança)
USER airflow
# ---------------------------------------------------------


# 1. Copia o requirements.txt para o contêiner
COPY requirements.txt .

# 2. Instala as dependências (incluindo o provedor docker, amazon e pandas)
RUN pip install --no-cache-dir -r requirements.txt

# 3. Limpeza (opcional, mas recomendado)
RUN rm requirements.txt
