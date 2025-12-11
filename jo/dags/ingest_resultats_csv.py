from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models import Connection
from airflow import settings
from sqlalchemy.orm import Session
from datetime import datetime
import pandas as pd
import os
from soda.scan import Scan


# ----------------------------
# ⚙️ Paramètres généraux
# ----------------------------
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 0
}


# ----------------------------
# 🧩 Fonctions Python
# ----------------------------
def ensure_postgres_connection():
    """Crée la connexion postgres_default si elle n'existe pas."""
    session: Session = settings.Session()
    conn_id = "postgres_default"

    if not session.query(Connection).filter(Connection.conn_id == conn_id).first():
        new_conn = Connection(
            conn_id=conn_id,
            conn_type='postgres',
            host='postgres_container',
            login='airflow',
            password='airflow',
            schema='airflow',
            port=5432
        )
        session.add(new_conn)
        session.commit()
        print(f"✅ Connexion {conn_id} créée automatiquement")
    else:
        print(f"⚠️ Connexion {conn_id} existe déjà")
    session.close()


def create_table_jo():
    """Lit et exécute le script SQL de création de table."""
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    sql_path = os.path.join(os.path.dirname(__file__), 'sql', 'create_jo.sql')
    with open(sql_path, 'r') as f:
        create_sql = f.read()

    cursor.execute(create_sql)
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Table 'jo' vérifiée ou créée avec succès.")


def load_csv_data():
    """Charge le CSV dans la table jo."""
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'fact_resultats_epreuves.csv')
    df = pd.read_csv(csv_path)

    # Nettoyage
    df = df.where(pd.notnull(df), None)
    for col in ['dt_creation', 'dt_modification', 'date_debut_edition', 'date_fin_edition']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    for col in ['est_epreuve_individuelle', 'est_epreuve_olympique', 'est_epreuve_ete', 'est_epreuve_handi']:
        if col in df.columns:
            df[col] = df[col].astype(bool)

    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    engine = pg_hook.get_sqlalchemy_engine()
    df.to_sql('jo', engine, if_exists='append', index=False)
    print("✅ Données insérées avec succès :", len(df), "lignes.")


def transform_data():
    """
    Transformation : filtrer les épreuves olympiques d’été,
    calculer le nombre d’épreuves par sport et par pays.
    Résultat stocké dans une table 'jo_transformed'.
    """
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    engine = pg_hook.get_sqlalchemy_engine()

    # Lecture depuis la table jo
    df = pd.read_sql("SELECT * FROM jo", engine)
    print(f"📥 {len(df)} lignes chargées depuis 'jo'.")

    # Filtrage : uniquement épreuves olympiques d’été
    df_filtered = df[
        (df['est_epreuve_olympique'] == True) &
        (df['est_epreuve_ete'] == True)
    ].copy()

    # Agrégation : nombre d'épreuves par sport et pays
    df_agg = (
        df_filtered.groupby(['sport', 'pays_en_base_resultats'])
        .agg(nb_epreuves=('id_epreuve', 'nunique'))
        .reset_index()
    )

    print(f"✅ {len(df_filtered)} lignes après filtrage.")
    print(f"📊 {len(df_agg)} lignes agrégées pour la table transformée.")

    # Sauvegarde dans PostgreSQL
    df_agg.to_sql('jo_transformed', engine, if_exists='replace', index=False)
    print("✅ Table 'jo_transformed' créée / mise à jour avec succès.")


# ----------------------------
# 🧪 Vérification Soda
# ----------------------------
def check_soda_installation():
    """Vérifie que Soda Core est bien installé et accessible."""
    try:
        scan = Scan()
        print("✅ Soda est bien installé et opérationnel :", scan)
    except ModuleNotFoundError:
        print("❌ Erreur : Soda n’est pas installé.")
    except Exception as e:
        print("⚠️ Soda installé mais erreur lors de l’import ou de l’utilisation :")
        print(str(e))


# ----------------------------
# 📊 Définition du DAG Airflow
# ----------------------------
with DAG(
    dag_id='ingest_resultats_csv',
    default_args=default_args,
    schedule_interval="0 8,20 * * *",
    catchup=False,
    tags=['jo', 'data-ingestion', 'soda']
) as dag:

    # Étape 1 : Connexion Postgres
    t_init_conn = PythonOperator(
        task_id='ensure_postgres_connection',
        python_callable=ensure_postgres_connection
    )

    # Étape 2 : Création table JO
    t0 = PythonOperator(
        task_id='create_table_jo',
        python_callable=create_table_jo
    )

    # Étape 3 : Ingestion CSV
    t1 = PythonOperator(
        task_id='load_csv_with_sqlalchemy',
        python_callable=load_csv_data
    )

    # Étape 4 : Contrôle qualité SODA sur données brutes
    t_soda_raw = BashOperator(
        task_id='soda_scan_raw',
        bash_command=(
            "soda scan "
            "-d airflow_pg "
            "-c /opt/airflow/dags/soda/configuration.yml "
            "/opt/airflow/dags/soda/soda_checks_raw.yml"
        )
    )

    # Étape 5 : Transformation des données
    t_transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data
    )

    # Étape 6 : Contrôle qualité SODA sur données transformées
    t_soda_transformed = BashOperator(
        task_id='soda_scan_transformed',
        bash_command=(
            "soda scan "
            "-d airflow_pg "
            "-c /opt/airflow/include/soda/configuration.yml"
            "/opt/airflow/include/soda/soda_checks_transformed.yml"
        )
    )

    # Étape 7 : Vérification de l’installation Soda
    t_soda = PythonOperator(
        task_id='check_soda_installation',
        python_callable=check_soda_installation
    )

    # 🔗 Ordre d’exécution
    (
        t_init_conn
        >> t0
        >> t1
        >> t_soda_raw
        >> t_transform
        >> t_soda_transformed
        >> t_soda
    )
