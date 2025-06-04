import streamlit as st
import pandas as pd
import psycopg2

# Connexion à PostgreSQL
conn = psycopg2.connect(
    host="postgres",       # ou "localhost" selon ta config
    database="airflow",
    user="airflow",
    password="airflow",
    port=5432
)

# Interface utilisateur
st.title("Exploration des données JO")

# Zone de saisie SQL
query = st.text_area("Écris ta requête SQL ici :", "SELECT COUNT(*) FROM jo;")

# Bouton pour exécuter la requête
if st.button("Exécuter"):
    try:
        df = pd.read_sql_query(query, conn)
        st.dataframe(df)
    except Exception as e:
        st.error(f"Erreur : {e}")
