from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
import pandas as pd
import os

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 0
}

with DAG(
    dag_id='ingest_resultats_csv',
    default_args=default_args,
    schedule_interval="*/2 * * * *",  # toutes les 2 minutes
    catchup=False
) as dag:

    def load_csv_data():
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'fact_resultats_epreuves.csv')
        df = pd.read_csv(csv_path)

        # Nettoyage des données
        df = df.where(pd.notnull(df), None)
        for col in ['dt_creation', 'dt_modification', 'date_debut_edition', 'date_fin_edition']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        for col in ['est_epreuve_individuelle', 'est_epreuve_olympique', 'est_epreuve_ete', 'est_epreuve_handi']:
            if col in df.columns:
                df[col] = df[col].astype(bool)

        # Connexion via SQLAlchemy
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        engine = pg_hook.get_sqlalchemy_engine()

        # Envoi dans la base (attention : la table doit exister !)
        df.to_sql('jo', engine, if_exists='append', index=False)
        print(df.head())  # Affiche les premières lignes du CSV dans les logs

    t1 = PythonOperator(
        task_id='load_csv_with_sqlalchemy',
        python_callable=load_csv_data
    )
