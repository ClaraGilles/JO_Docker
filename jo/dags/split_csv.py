import pandas as pd
import os

def split_csv(input_file, output_file1, output_file2):
    """
    Divise un fichier CSV en deux fichiers égaux.
    :param input_file: Le fichier CSV source.
    :param output_file1: Le premier fichier de sortie.
    :param output_file2: Le second fichier de sortie.
    """
    # Lire le fichier CSV dans un DataFrame
    df = pd.read_csv(input_file)

    # Calculer le point de division
    split_point = len(df) // 2

    # Diviser le DataFrame en deux parties
    df1 = df[:split_point]
    df2 = df[split_point:]

    # Sauvegarder les deux parties dans des nouveaux fichiers CSV
    df1.to_csv(output_file1, index=False)
    df2.to_csv(output_file2, index=False)

    print(f"Le fichier a été divisé en deux parties : '{output_file1}' et '{output_file2}'")

if __name__ == '__main__':
    # Définir les chemins des fichiers (dans le dossier data)
    input_file = './dags/data/fact_resultats_epreuves.csv'
    output_file1 = './dags/data/fact_resultats_epreuves_part1.csv'
    output_file2 = './dags/data/fact_resultats_epreuves_part2.csv'

    # Appeler la fonction pour diviser le CSV
    split_csv(input_file, output_file1, output_file2)
