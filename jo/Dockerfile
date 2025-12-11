# Dockerfile d'Airflow avec des dépendances supplémentaires
FROM apache/airflow:2.10.3

# Utilisateur non-root pour la sécurité (redevient root si besoin plus bas)
USER airflow

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
