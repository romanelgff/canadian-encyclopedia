# Web scrapping (The Canadian Encyclopedia)
Web-based content analysis of the pages of the Canadian encyclopedia with Python.

## English description

This project is broken down into:
* a scrapping part with the extraction of information in a set of web pages;
* a serialization of extracted content as a .pick file;
* an analysis section with the construction of a DTM and query tools on the corpus.

The **scraping.py** file is dedicated to the scraping part while the **analyse.py**  file contains the analyses made on the scraped website "The Canadian Encyclopedia" (word clouds, creation of a DTM class allowing tag management). The **stop_words.txt** file contains English stop words that we don't want to include in our analyses. Finally, the file **infos.pick** includes the extracted data.


## French description

Ce projet est décomposé en :
* une partie scrapping avec l’extraction d’informations dans un ensemble de pages web ;
* la sérialisation du contenu extrait sous forme d’un fichier .pick;
* une partie analyse avec la construction d’une DTM et d’outils de requêtes sur le corpus.

Le fichier **scraping.py** est dédié à la partie "scraping" du projet tandis que le fichier **analyse.py** contient les analyses faites sur le site web scrapé (nuages de mots, création d'une clase DTM permettant la gestion des balises). Le fichier **stop_words.txt** contient une liste de mots vides anglais que nous ne voulons pas inclure dans nos analyses. Enfin, le fichier **infos.pick** est le fichier comportant les données extraites.
