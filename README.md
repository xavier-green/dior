﻿# Projet ChatBot Dior

Prototype de ChatBot permettant d'accéder aux données précises de la BDD de Dior en posant des questions en langage naturel. Par exemple, permet der répondre aux questions "Combien de Lady Dior vendu cette semaine" ou "Quelle est la couverture de stock en chemises"
 * Tous les programmes sont modifiables avec un simple éditeur de texte comme le Bloc-note de Windows *

## Getting started

Ce projet est scindé en quatre parties :
1. L'application swift, sur l'iPhone des exécutifs
2. Le Bot en Python / Flask, sur une VM Windows chez Dior
3. L'API fasttext, sur une VM Ubuntu chez OVH
4. La BDD MSSQL, sur une VM Windows chez Dior

La quatrième partie est laissée aux bons soins de Dior.

### Lancer l'API de OVH (folder ovh)

Commandes à effectuer pour installer les modules nécessaires :

```
pip install fasttext
python fasttext_server.py
```

Pour utiliser l'API Rest :

```
GET sur /{mot} : Retourne le vecteur (de dim 300) associé au mot (vecteur nul sinon)
POST sur / avec un body = {"words":["madrid","chien"]} : Retourne un tableau des vecteurs associés au mots du body
```

### Installation de l'API Principale

Tout d'abord cloner le dépôt à l'aide de Git (Git bash sous Windows)
`git clone <depot_distant>`
et installer python3.6 (avec Anaconda sur Windows)

Commandes à effectuer pour pouvoir lancer le bot (dans cmd.exe):

`pip install -r requirements.txt`

Il faut ensuite créer un service dans le task scheduler de windows (crontab) qui run les script .bat (launch.bat et dumps_desc.bat).
Vous pouvez lancer le ChatBot (si non lancé avec le Task schedueler) en démarrant launcher.bat ou avec la commande suivante :
```
python start.py
```

Il faut enfin copier ou créer le fichier config.py, à mettre dans le dossier principal. Ce fichier est à remplir de la façon suivante :
```
fasttext_url = "url_server_fasttext"
SQL_Server = "url_server_SQL"
SQL_Username = "username_SQL"
SQL_Password = "password_SQL"
SQL_Database = "database_SQL"
```

### Utilisation de l'API Principale

POST sur / avec un body = {"sentence":"combien avons nous vendu de sac hier","seuil":500000} :: Retourne un dictionnaire contenant le 'anwser' qui est ce qui sera retourné au user sur l'app et 'details' qui montre les informations supplémentaires lorsque le user clique sur la réponse du bot
--> Sentence contient la phrase de l'utilisateur, le seuil est le seuil de transactions exceptionnelles

GET /admin/logs :: Tableau avec tous les logs de l'app (date-question-requête SQL-réponse)

### Modifications de l'accès SQL

Pour modifier l'authentification SQL, on change le fichier config.py.
Il contient les variables SQL_Server, SQL_Username, SQL_Password et SQL_Database

Tables utilisées : dans sql/tables.py se trouve l'ensemble des tables.

<table_name_interne> = table(<TABLE_NAME_SQL>, <TABLE_Prefix>, <Alias>, [<colonne1>, <colonne2>,...])

Si les colonnes de la base changent, il faut modifier ce fichier ainsi que tous les fichiers .py aux lignes où on trouve table_name_interne et colonne.

Vous pouvez rechercher quels fichiers doivent être modifiés dans Git Bash avec `git grep -e ".*<table_name>.*<colonne>.*`

## Architecture du code

Start.py lancer le bot et gère l'ordre dans lequel sont exécutées toutes les fonctions. Cet ordre est le suivant :

1. Traduction des mots du glossaire de Dior
2. Extraction des mots-clés utiles et nettoyage de la phrase
3. Extraction de l'intent (vente/stock/boutique/vendeur)
4. Ecriture de la requête à partir de l'intent et des mots-clés
5. Traitement et envoit de la réponse reçue, avec les détails

### Annexes

Contient toutes les fonctions annexes, que ce soit pour la mise en forme des dates (passer JJ/MM/AAAA), les séparateurs de milliers, ou une écriture plus rapide du pop-up d'informations.

### Data

Contient intent-data, les données utilisées pour entraîner le ML du bot, et le glossaire utilisé pour traduire les mots du vocabulaire spécifique de Dior.

### Extraction

Contient glossaire.py, qui traduit les mots spécifiques à Dior en mots utiles pour la requête (ex: horlo > watches), ainsi que les fichiers d'extractions des mots-clés de contexte boutique, date, geo, produit.

### Intent

Contient intent.py et train.py qui se chargent du ML, et un fichier par intent pour écrire la requête correspondant à l'intent. Par exemple, une question "Quelle est ma meilleure boutique ?" correspondra à l'intent "boutique" et sa requête sera donc écrite dans boutique.py

### OVH

Contient le serveur fasttext.

### SQL

Contient tables.py, la liste des tables auxquelles on fait des requêtes sous forme d'objets, et request.py, une classe de requêtes utilisées pour écrire plus facilement des requêtes.

### Templates

Contient le HTML pour la page /admin/logs qui permet d'accéder à l'historique des questions posées

## Authors

* **Solen Le Roux--Couloigner**
* **Rémi Garde**
* **Xavier Green**