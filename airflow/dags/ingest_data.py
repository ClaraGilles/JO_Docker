from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine

def ingest():
    df = pd.read_csv("/opt/airflow/dags/fact_resultats_epreuves.csv")
    engine = create_engine("postgresql+psycopg2://user:pass@db:5432/mydb")
    df.to_sql("jo_2024", engine, if_exists="append", index=False)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

with DAG("ingest_every_hour", schedule_interval='@hourly', default_args=default_args, catchup=False) as dag:
    ingest_task = PythonOperator(
        task_id="ingest_data",
        python_callable=ingest
    )
