import streamlit as st
import pandas as pd
import sqlalchemy
import os

st.title("SQL Playground")

query = st.text_area("Entrez votre requête SQL")

if st.button("Exécuter"):
    engine = sqlalchemy.create_engine(f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}")
    try:
        df = pd.read_sql_query(query, engine)
        st.dataframe(df)
    except Exception as e:
        st.error(f"Erreur : {e}")
