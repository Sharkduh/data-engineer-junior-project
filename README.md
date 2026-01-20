# 🚀 Data Engineer Junior Project: Pipeline de Ingestão e Orquestração

Este repositório contém uma solução completa de Engenharia de Dados focada na construção de um **Data Lake** funcional, utilizando práticas de containerização, armazenamento de objetos e orquestração de fluxos de trabalho.

O projeto automatiza o ciclo de vida do dado: desde a extração bruta (Raw), passando pelo refinamento (Silver/Trusted), até a disponibilização em um Data Mart (Gold) pronto para análise.



---

## 🛠️ Tecnologias e Ferramentas

| Ferramenta | Uso no Projeto |
| :--- | :--- |
| **Python 3.x** | Linguagem principal para processamento e lógica de scripts. |
| **Apache Airflow** | Orquestrador de workflows (DAGs) e agendamento de tarefas. |
| **MinIO** | Data Lake local compatível com S3 para armazenamento de objetos. |
| **Docker & Compose** | Containerização de toda a stack para portabilidade. |
| **Shell Scripting** | Automação de rotinas de setup e execução de testes. |
| **PostgreSQL** | Banco de dados de metadados para o Airflow. |

---

## 🧠 Por que usamos Airflow e DAGs?

A escolha do **Apache Airflow** como orquestrador central é estratégica por diversos motivos técnicos que elevam a robustez do projeto:

1.  **DAGs (Directed Acyclic Graphs):** As tarefas são organizadas em Grafos Acíclicos Dirigidos. Isso garante que as dependências sejam respeitadas (ex: o script de `transformation.py` nunca será executado antes que o `extract_data.py` termine com sucesso).
2.  **Idempotência e Retentativas:** O Airflow permite configurar políticas de *retry*. Se uma API falhar momentaneamente, a DAG tentará novamente de forma automática sem duplicar dados.
3.  **Monitoramento Centralizado:** Através da interface web, é possível visualizar gargalos, conferir logs detalhados (armazenados em `logs/`) e gerenciar o histórico de execuções.
4.  **Escalabilidade:** A arquitetura modular permite que o pipeline cresça de scripts simples para processos complexos distribuídos em múltiplos containers.

---

## 📂 Estrutura do Projeto

```text
├── dags/
│   └── ingestion_dag.py          # Definição lógica do pipeline no Airflow
├── scripts/                      # Módulos Python de processamento
│   ├── extract_data.py           # Ingestão de dados da fonte
│   ├── refine_data.py            # Limpeza e normalização (Camada Silver)
│   ├── transformation.py         # Regras de negócio (Camada Gold)
│   ├── setup_minio.py            # Provisionamento automático de Buckets
│   ├── check_datamart.py         # Validação de integridade dos dados
│   └── upload_override.py        # Gestão de sobreposição de arquivos no storage
├── Dockerfile                    # Blueprint da imagem personalizada
├── docker-compose.yml            # Orquestração (Airflow + Postgres + MinIO)
├── requirements.txt              # Dependências Python do projeto
└── run_test.sh                   # Script Bash para validação e testes
