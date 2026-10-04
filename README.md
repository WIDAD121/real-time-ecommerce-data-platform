\# Real-Time E-Commerce Data Platform



End-to-end data engineering project on the Olist Brazilian e-commerce

dataset (\~550,000 rows across 9 tables): ingestion, a tested

PostgreSQL warehouse, dbt transformations, PySpark batch processing,

Kafka + Spark Structured Streaming for real-time analytics, Airflow

orchestration, a Metabase dashboard, and a churn prediction model.



\## Architecture



Raw CSVs -> PostgreSQL -> dbt models -> star schema warehouse

&#x20;                                     -> PySpark (validated batch job)

Kafka producer -> orders topic -> Spark Structured Streaming (live)

Airflow DAG orchestrates the batch side daily; all 26 tests must pass.

Metabase dashboard and a Random Forest churn model sit on top.



\## Stack



PostgreSQL 16, dbt, PySpark, Apache Kafka (KRaft), Spark Structured

Streaming, Apache Airflow, Metabase, scikit-learn, pytest, Docker Compose



\## Results



\- 26/26 automated data-quality + warehouse tests passing

\- dw.fact\_sales revenue matches raw data to the cent ($13,591,643.70)

\- PySpark batch job cross-validated against the SQL warehouse

\- Airflow DAG: 5 tasks, full pipeline rebuild in 48 seconds, unattended

\- Churn model: 85% accuracy, MCC 0.685, with a documented

&#x20; feature-importance investigation



\## Quickstart



docker compose up -d

python -m venv .venv

.venv\\Scripts\\activate

pip install -r requirements.txt

docker exec -i ecommerce-postgres psql -U ecommerce\_user -d ecommerce < sql\\01\_create\_schema.sql

python src\\ingestion\\load\_to\_postgres.py

python -m pytest tests -v



\## Project Structure



\- sql/ - schema, views, star schema

\- src/ingestion/ - CSV to PostgreSQL loader

\- src/spark/ - batch and streaming Spark jobs

\- src/kafka/ - producer and consumer

\- src/ml/ - churn model

\- tests/ - 26 pytest data-quality and warehouse tests

\- ecommerce\_dbt/ - dbt models, tests, docs

\- airflow/dags/ - orchestration DAG

\- docker-compose\*.yml - Postgres/Kafka, Airflow, Metabase



\## Notable Engineering Decisions



\- Idempotent ingestion, safe to re-run without duplicating data

\- Star schema (fact\_sales plus 4 dimension tables), rebuilt from

&#x20; scratch on demand

\- dbt source()-based lineage, with auto-generated documentation

\- Airflow caught a real schema bug invisible in the live database

\- MCC used over plain accuracy due to class imbalance in churn labels

