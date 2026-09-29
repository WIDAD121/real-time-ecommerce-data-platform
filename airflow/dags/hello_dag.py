from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="hello_ecommerce",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    BashOperator(task_id="say_hello", bash_command="echo Airflow works")