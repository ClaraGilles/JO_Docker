# Dockerfile d'Airflow
FROM apache/airflow:2.10.3

# Utilisateur non-root pour la sécurité (redevient root si besoin plus bas)
USER airflow

# Installation des dépendances Python requises (seulement pour Airflow ici)
RUN pip install --no-cache-dir psycopg2-binary
