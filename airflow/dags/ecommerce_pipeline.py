import os
from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine

PROJECT = "/opt/airflow/project"


def run_sql_files(*filenames):
    engine = create_engine(os.environ["DATABASE_URL"])
    for name in filenames:
        sql = (Path(PROJECT) / "sql" / name).read_text(encoding="utf-8-sig")
        with engine.begin() as conn:
            conn.exec_driver_sql(sql)
        print(f"Ran {name}")


with DAG(
    dag_id="ecommerce_batch_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
) as dag:

    create_schema = PythonOperator(
        task_id="create_schema",
        python_callable=run_sql_files,
        op_args=["01_create_schema.sql"],
    )

    load_data = BashOperator(
        task_id="load_data",
        bash_command=f"cd {PROJECT} && python src/ingestion/load_to_postgres.py",
    )

    build_views = PythonOperator(
        task_id="build_views",
        python_callable=run_sql_files,
        op_args=["02_analytics_views.sql", "03_category_view_en.sql"],
    )

    build_warehouse = PythonOperator(
        task_id="build_warehouse",
        python_callable=run_sql_files,
        op_args=["04_star_schema.sql"],
    )

    run_tests = BashOperator(
        task_id="run_tests",
        bash_command=f"cd {PROJECT} && python -m pytest tests -v -p no:cacheprovider",
    )

    create_schema >> load_data >> build_views >> build_warehouse >> run_tests