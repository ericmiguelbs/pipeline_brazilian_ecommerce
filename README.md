# Pipeline de Dados – Brazilian E-Commerce (Olist)

Pipeline de dados completo sobre o dataset público da Olist no Kaggle, seguindo a arquitetura **Medallion** (Bronze → Silver → Gold), orquestrado com **Apache Airflow** e servido em um dashboard **Streamlit**.

---

## Arquitetura

```
Kaggle (KaggleHub)
      │
      ▼
┌─────────────┐     PySpark      ┌─────────────┐     PySpark      ┌──────────────┐
│   Bronze    │ ──────────────▶  │   Silver    │ ──────────────▶  │     Gold     │
│  (Parquet)  │                  │  (Parquet)  │                  │ (PostgreSQL) │
└─────────────┘                  └─────────────┘                  └──────────────┘
                                                                          │
                                                                          ▼
                                                                   ┌────────────┐
                                                                   │ Streamlit  │
                                                                   │ Dashboard  │
                                                                   └────────────┘
```

| Camada   | Responsabilidade                                                          |
|----------|---------------------------------------------------------------------------|
| **Bronze** | Ingestão bruta dos CSVs via KaggleHub, salvo em Parquet com metadados de ingestão |
| **Silver** | Limpeza, tipagem e padronização dos dados por domínio                    |
| **Gold**   | Modelagem dimensional (fatos e dimensões) carregada no PostgreSQL        |

---

## Stack

| Tecnologia        | Versão    | Uso                                    |
|-------------------|-----------|----------------------------------------|
| Apache Airflow    | 2.9.1     | Orquestração do pipeline               |
| PySpark           | 3.5.1     | Processamento distribuído (Bronze/Silver) |
| PostgreSQL        | 16        | Data Warehouse (camada Gold)           |
| Streamlit         | latest    | Dashboard analítico                    |
| KaggleHub         | latest    | Download automático do dataset         |
| pandas            | 2.2.3     | Manipulação de dados (Gold → DW)       |
| Redis             | 7.2       | Broker do Celery Executor (Airflow)    |
| Docker / Compose  | –         | Infraestrutura local                   |

---

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e Docker Compose
- Conta no [Kaggle](https://www.kaggle.com/) com API token gerado

---

## Configuração

### 1. Variáveis de ambiente

Copie o arquivo de exemplo e preencha os valores:

```bash
cp .env.example .env
```

Variáveis obrigatórias antes de subir os containers:

| Variável | Descrição |
|----------|-----------|
| `KAGGLE_API_TOKEN` | Token JSON da API do Kaggle (`~/.kaggle/kaggle.json`) |
| `FERNET_KEY` | Chave de criptografia do Airflow (gere com o comando abaixo) |
| `POSTGRES_PASSWORD` | Senha do banco Gold (mude em produção) |

Gerando a `FERNET_KEY`:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 2. Inicializar o ambiente

```bash
# Inicializa banco e cria usuário admin do Airflow
docker compose up airflow-init

# Sobe todos os serviços em background
docker compose up -d
```

---

## Serviços e Portas

| Serviço               | URL / Porta               | Credenciais padrão       |
|-----------------------|---------------------------|--------------------------|
| Airflow Webserver     | http://localhost:8080     | airflow / airflow        |
| Streamlit Dashboard   | http://localhost:8501     | –                        |
| PostgreSQL (Gold DW)  | localhost:5432            | postgres / postgres      |

---

## Estrutura do Projeto

```
.
├── dags/
│   └── dag_dados_olist.py      # DAG principal (Bronze → Silver → Gold)
├── src/
│   ├── bronze/
│   │   └── data_ingestao.py    # Download e ingestão via KaggleHub
│   ├── silver/
│   │   ├── clean_*.py          # Limpeza por domínio
│   │   └── run_silver.py       # Entry point da camada Silver
│   ├── gold/
│   │   ├── dim_*.py            # Dimensões (clientes, produtos, vendedores, calendário)
│   │   ├── fato_*.py           # Fatos (vendas, pagamentos)
│   │   └── run_gold.py         # Entry point da camada Gold
│   ├── app/
│   │   └── app.py              # Dashboard Streamlit
│   ├── utils/
│   │   └── database.py         # Conexão e carga no PostgreSQL
│   └── config.py               # Configuração da SparkSession
├── dados/
│   ├── bronze/                 # Parquet bruto
│   └── silver/                 # Parquet limpo
├── config/
│   └── airflow.cfg             # Configurações customizadas do Airflow
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## DAG – `pipeline_medalhao_olist`

```
inicio_pipeline
      │
      ▼
camada_bronze_ingestao       # src/bronze/data_ingestao.py
      │
      ▼
camada_silver_tratamento     # src/silver/run_silver.py
      │
      ▼
camada_gold_metricas         # src/gold/run_gold.py
      │
      ▼
fim_pipeline
```

- **Schedule:** diário (`@daily`)
- **Retries:** 2 tentativas com intervalo de 2 minutos
- **Tags:** `lakehouse`, `medalhao`, `producao`

---

## Dataset

[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — ~100 mil pedidos de 2016 a 2018, com informações de clientes, produtos, vendedores, pagamentos e avaliações.

Tabelas ingeridas:

- `olist_customers_dataset`
- `olist_geolocation_dataset`
- `olist_orders_dataset`
- `olist_order_items_dataset`
- `olist_order_payments_dataset`
- `olist_order_reviews_dataset`
- `olist_products_dataset`
- `olist_sellers_dataset`

---

## Desenvolvimento local (sem Docker)

```bash
# Criar e ativar virtualenv
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

pip install -r requirements.txt

# Rodar manualmente cada camada
python src/bronze/data_ingestao.py
python src/silver/run_silver.py
python src/gold/run_gold.py
```

> Certifique-se de que as variáveis do `.env` estão preenchidas e que o PostgreSQL está acessível em `localhost:5432`.
