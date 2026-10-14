from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

default_args = {
    'owner': 'dados_olist',
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    dag_id='pipeline_medalhao_olist',
    default_args=default_args,
    description='Orquestração das camadas Bronze, Silver e Gold',
    start_date=datetime(2026, 9, 1),
    schedule='@daily',
    catchup=False,
    tags=['lakehouse', 'medalhao', 'producao']   
) as dag:

    inicio = EmptyOperator(task_id='inicio_pipeline')

    camada_bronze = BashOperator(
        task_id='camada_bronze_ingestao',
        bash_command='export PYTHONPATH="/opt/airflow" && python /opt/airflow/src/bronze/data_ingestao.py'
    )

    camada_silver = BashOperator(
        task_id='camada_silver_tratamento',
        bash_command='export PYTHONPATH="/opt/airflow" && python /opt/airflow/src/silver/run_silver.py'
    )

    camada_gold = BashOperator(
        task_id='camada_gold_metricas',
        bash_command='export PYTHONPATH="/opt/airflow" && python /opt/airflow/src/gold/run_gold.py'
    )

    fim = EmptyOperator(task_id='fim_pipeline')

    inicio >> camada_bronze >> camada_silver >> camada_gold >> fim