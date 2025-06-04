Partie 1 : Découverte de Docker (Création d’une image Docker basique)

Quelles sont les étapes pour construire une image Docker à partir d’un fichier Dockerfile ?
Quel est le rôle de la commande docker build ? Donnez un exemple de syntaxe.
Quelle est la différence entre les instructions FROM, WORKDIR et CMD dans un fichier Dockerfile ?
Pourquoi est-il important de spécifier une image de base dans le fichier Dockerfile ?
Une fois l’image construite, comment pouvez-vous exécuter un conteneur basé sur cette image ?
Si vous modifiez le fichier source Python utilisé dans le conteneur, que devez-vous faire pour refléter ces modifications dans votre conteneur ?
Partie 2 : Découverte de Docker-Compose (Architecture multi-conteneurs)

Vous devez orchestrer une architecture comprenant deux conteneurs :

Un service PostgreSQL.
Une API Flask permettant de communiquer avec la base de données.
Quelles informations doivent être définies dans le fichier docker-compose.yml pour configurer un conteneur PostgreSQL ?
À quoi sert la directive depends_on dans un fichier docker-compose.yml ?
Comment pouvez-vous vous assurer que votre API Flask est correctement connectée à la base de données PostgreSQL ?
Que fait la commande docker-compose up --build ?
Une fois votre architecture en marche, comment vérifier que l’API Flask renvoie la bonne réponse depuis le navigateur ou via un outil comme curl ?
Pourquoi est-il recommandé d’utiliser Docker-Compose au lieu de démarrer manuellement chaque conteneur avec Docker ?
Partie 3 : Projet final (Chaîne complète de traitement de données)

Vous devez créer une chaîne complète de traitement de données comprenant :

Un conteneur PostgreSQL pour stocker les données.
Un conteneur Python exécutant un script ETL (Extraction, Transformation, Chargement).
Un conteneur Streamlit pour afficher les données stockées dans la base de données.
