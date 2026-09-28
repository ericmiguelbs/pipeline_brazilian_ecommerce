from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG (
    dag_id='primeira_DAG',
    start_date=datetime(2026,10,1),
    schedule='@daily',
    doc_md=__doc__
):
    start = EmptyOperator(task_id="start")
    hello = BashOperator(task_id="hello",bash_command="echo hello world")
    end = EmptyOperator(task_id="end")

(start >> hello >> end)

