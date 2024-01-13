# Sommaire

1. [Installation](#installation)
    1. [Prérequis](#prérequis)
    2. [Installation des dépendances](#installation-des-dépendances)
    3. [Téléchargement du pilote ChromeDriver](#téléchargement-du-pilote-chromedriver)
2. [Exécution du Script](#exécution-du-script)
3. [Nettoyage des données](#nettoyage-des-données)
4. [Données Scrapées](#données-scrapées)
5. [Configuration](#configuration)
6. [Auteur](#auteur)


# Installation
## Tout ces commandes et installation sont possible sous Windows

Avant d'exécuter le script, assurez-vous d'avoir les éléments suivants installés :

## Prérequis

**Python :** Assurez-vous d'avoir Python installé sur votre machine. Vous pouvez télécharger la dernière version [ici](https://www.python.org/downloads/). Lors de l'installation, assurez-vous de cocher l'option "Add Python to PATH" pour faciliter l'accès à Python depuis n'importe où dans votre terminal. Si vous avez omis cette étape, voici comment le faire :

1. Lors de l'installation de Python, cochez la case "Add Python to PATH" avant de cliquer sur "Install Now".


2.  Vous pouvez également ajouter manuellement Python au PATH en ajoutant ces deux variables d'environnement dans votre système si vous n'avez pas cocher la case "Add Python to PATH" :

- Sur Windows : 

    ```
    C:\Users\{user}\AppData\Local\Programs\Python\Python312\
    ```
    ```
    C:\Users\{user}\AppData\Local\Programs\Python\Python312\Scripts\
    ```

- Sur Macos / Linux : 

    Pour le chemin du binaire Python :
    ```bash
    export PATH="/chemin/vers/python3.x/bin:$PATH"
    ```

    Pour le chemin du dossier "Scripts" qui contient pip :

    ```bash
    export PATH="/chemin/vers/python3.x/bin/Scripts:$PATH"
    ```

Vous pouvez vérifier si Python est installé en exécutant la commande suivante dans votre terminal :

```bash
python --version
```

Sur macOS/Linux, la commande peut être :

```bash
python3 --version
```

**Gestionnaire de paquets pip :** Pip est généralement inclus avec l'installation de Python. Vous pouvez vérifier s'il est installé en exécutant la commande suivante dans votre terminal :


- Sur Windows : 
```bash
pip --version
```

- Sur macOS/Linux, la commande peut être :

```
pip3 --version
```

Si pip n'est pas installé, vous pouvez suivre les instructions [ici](https://pip.pypa.io/en/stable/installation/) pour l'installer.

## Environnement Virtuel

Pour exécuter ce projet dans un environnement virtuel, suivez ces étapes :

1. **Créer l'environnement virtuel :**
   Utilisez la commande suivante pour créer un environnement virtuel. Assurez-vous d'avoir installé `virtualenv` au préalable.

   - Sur Windows :
     ```bash
     python -m venv venv
     ```

   - Sur macOS/Linux :
     ```bash
     python3 -m venv venv
     ```

2. **Activer l'environnement virtuel :**
   - Sur Windows :
     ```bash
     .\venv\Scripts\activate
     ```

   - Sur macOS/Linux :
     ```bash
     source venv/bin/activate
     ```

   Vous verrez le nom de votre environnement virtuel apparaître dans le terminal, indiquant qu'il est activé.

3. **Désactiver l'environnement virtuel :**

   - Pour Windows, macOS et Linux:

      ```bash
       deactivate
      ```

## Installation les dépendances

Après avoir installé Python, pip et avoir mit en place l'environnement virtuel, vous pouvez installer les dépendances nécessaires en utilisant le fichier **requirements.txt** fourni. <br> Exécutez la commande suivante dans le répertoire du projet :

- Sur Windows :

```bash
pip install -r requirements.txt
```

- Sur macOS/Linux, vous pouvez utiliser la commande suivante :

```bash
pip3 install -r requirements.txt
```

Cette commande installera toutes les bibliothèques Python nécessaires pour exécuter le script.


## Téléchargement du pilote ChromeDriver

Le script utilise ChromeDriver pour automatiser le navigateur Chrome. Si vous ne l'avez pas déjà installé, le script téléchargera automatiquement le pilote ChromeDriver lors de sa première exécution. Assurez-vous d'avoir une connexion Internet active lors de l'exécution du script pour effectuer ce téléchargement.

## Commandes

⚠️Par défaut le script crée un fichier data.json et un dossier Covers si il n'y en pas quand vous utiliser une commande pour scrap une page.⚠️

Le script prend en charge plusieurs commandes pour différents types de scraping. Voici la liste des commandes disponibles :

## Interface

Cette commande ouvre une interface graphique pour le scrapper pour eviter de taper les commandes :
⚠️ Cette commande n'est pas encore stable, des bugs peuvents ce produire ⚠️
⚠️ Toutes les commandes ne sont pas disponible sur l'interface graphique ⚠️

```bash
python scraper.py interface
```

### Clean: 
Cette commande nettoie le fichier data.json et le dossier Covers. Utilisez la commande suivante dans le terminal :

```bash
python scraper.py clean
```

### Clean All: 
Cette commande nettoie le fichier data.json, le dossier Tri et le dossier Covers. Utilisez la commande suivante dans le terminal :

```bash
python scraper.py clean-all
```

### Série [genre]: 

Cette commande scrape les pages de séries en fonction du genre spécifié. Remplacez [genre] par le genre de votre choix parmi les suivants : 
```action, animation, aventure, biopic, comedie, comedie-dramatique, drame, epouvante-horreur, espionnage, famille, fantastique, historique, judiciaire, policier, romance, science-fiction, thriller``` 

Utilisez la commande suivante dans le terminal :
```bash
python scraper.py serie [genre]
```

### Film [genre]:
Cette commande scrape les pages de films en fonction du genre spécifié. Remplacez [genre] par le genre de votre choix parmi les suivants : ```
action, animation, aventure, biopic, comedie, comedie-dramatique, drame, epouvante-horreur, famille, fantastique, guerre, historique, musical, policier, romance, science-fiction, thriller, western ```

Utilisez la commande suivante dans le terminal :
```bash
python scraper.py film [genre]
```

## Serie-all

La commande `serie-all` permet de scraper toutes les pages des séries pour chaque genre spécifié.

Utilisez la commande suivante dans le terminal :

```bash
python scraper.py serie-all
```

## Film-all

La commande film-all permet de scraper toutes les pages des meilleurs films pour chaque genre spécifié.

Utilisez la commande suivante dans le terminal :
```bash
python scraper.py film-all
```

## All

La commande all permet de scraper toutes les pages, à la fois des séries et des films, pour chaque genre spécifié. Elle fait ensuite la commande tri pour trier les series et les films séparement. Ensuite elle exécute la commande clean pour supprimer le dossier Covers vide et data.json.

```bash
python scraper.py all
```

## Everyfilm

La commande everyfilm permet de scraper toutes les pages des films sans genre spécifique.
⚠️ Cette commande prend beaucoup de temps à s'executer entierement ⚠️

```bash
python scraper.py everyfilm
```

## Everyserie

La commande everyserie permet de scraper toutes les pages des series sans genre spécifique.
⚠️ Cette commande prend beaucoup de temps à s'executer entierement ⚠️

```bash
python scraper.py everyserie
```

## Everyall

La commande everyall permet de scraper toutes les pages des films et des series sans genre spécifique. Elle fait ensuite la commande tri pour trier les series et les films séparement. Ensuite elle exécute la commande clean pour supprimer le dossier Covers vide et data.json.
⚠️ Cette commande prend beaucoup de temps à s'executer entierement ⚠️

```bash
python scraper.py everyall
```


### Tri :

Cette commmande tri tout les films/séries dans le fichier data.json et le met séparement dans un fichier film.json et serie.json dans un dossier Tri

Utilisez la commande suivante dans le terminal :
```bash
python scraper.py tri
```

### Help:
Cette commande affiche la liste des commandes disponibles et des genres pris en charge. Utilisez la commande suivante dans le terminal :
```bash
python scraper.py help
```

## Données Scrapées

Le script récupère les informations suivantes pour chaque film :

- **films_number :** Le nombre total de films récupérés.

- **films :** Une liste d'objets représentant chaque film. Chaque objet contient les détails suivants :
    - **type :** Serie
    - **title :** Le titre du film.
    - **release_date :** La date de sortie du film.
    - **length :** La durée du film.
    - **type :** Le genre du film.
    - **director :** Le réalisateur du film.
    - **actors :** Une liste des acteurs principaux du film.
    - **synopsis :** Le synopsis du film.
    - **sessions :** Le nombre de sessions pour le film.
    - **rating :** Un objet contenant les notes attribuées au film par les critiques et le public.
        - **critics :** La note attribuée par les critiques.
        - **audience :** La note attribuée par le public.
    - **image :** Le chemin d'accès à l'image de couverture du film.

Voici un exemple de données pour un film :
```json
{
    "title": "Les Trois Mousquetaires: Milady",
    "release_date": "13 décembre 2023",
    "length": "1h 55min",
    "type": "Aventure, Historique",
    "director": "Martin Bourboulon",
    "actors": [
        "François Civil",
        "Vincent Cassel",
        "Romain Duris"
    ],
    "synopsis": "Du Louvre au Palais de Buckingham, des bas-fonds de Paris au siège de La Rochelle… dans un Royaume divisé par les guerres de religion et menacé d’invasion par l’Angleterre, une poignée d’hommes et de femmes vont croiser leurs épées et lier leur destin à celui de la France.",
    "sessions": 1000,
    "rating": {
        "critics": 3.3,
        "audience": 3.7
    },
    "image": "Covers/LesTroisMousquetairesMilady.jpg"
}
```

## Configuration

Le fichier de configuration **config.ini** est essentiel pour personnaliser le comportement du script. 
Voici comment le configurer :

```ini
[Urls]

page_url_film_cinema = https://www.allocine.fr/film/aucinema/?page=
start_page_film_cinema = 1
max_page_number_film_cinema = 14


[Files]
output_file = data.json
```


Assurez-vous d'ajuster les valeurs en fonction de vos besoins :

- `page_url` : Spécifiez l'URL des pages à parcourir.
(Ne fonctionne que sur la page au cinéma d'Allociné pour l'instant)
- `start_page` : Définissez la page précise où le script va commencer à parcourir le site.<br>
- `max_page` : Définissez la page où le script va s'arrêter
(⚠️ La max_page est par défaut au maximum, ne dépassez pas le maximum ⚠️)
        
Le fichier de configuration est prêt à être utilisé. Vous pouvez ajuster ces valeurs à tout moment en fonction de vos besoins spécifiques.

Si le fichier config.ini est déjà créé, assurez-vous simplement que les valeurs sont correctement configurées en fonction de vos besoins.

🚀 C'est tout ! Vous êtes prêt à exécuter le script une fois que toutes les dépendances sont installées. 🚀

## Auteur

Ce script a été créé par [Luxlas558](https://github.com/Luxlas558).

Pour toute question, suggestion ou contribution, n'hésitez pas à me contacter :

- GitHub : [Luxlas558](https://github.com/Luxlas558)
- Discord : Luxlas

