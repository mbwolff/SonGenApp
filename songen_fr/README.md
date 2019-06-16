# SonGenApp français
## Un générateur de sonnets en français
### Basé sur [cette contribution](https://github.com/mbwolff/Classique-inconnu) à [NaNoGenMo 2018](https://github.com/NaNoGenMo/2018)

Le code pour ce projet génère des sonnets en alexandrins avec des vers dans le corpus du [Théâtre Classique](http://www.theatre-classique.fr). On peut l'essayer [ici](http://markwolff.name/wp/digital-humanities-2/invent-your-own-sonnet-using-analytic-tools-to-synthesize-texts/).

En voici la procédure:

1. Gratter les liens des textes de [cette page](http://www.theatre-classique.fr/pages/programmes/PageEdition.php) et télécharger les fichiers XML pour construire un corpus.
2. Créer un espace vectoriel pour tous les mots dans le corpus avec [la module Word2Vec de Gensim](https://radimrehurek.com/gensim/models/word2vec.html). Les mots sont lemmatisés avec [TreeTagger](https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/) pour simplifier l'espace vectoriel.
3. Créer une [matrice tf-idf](https://scikit-learn.org/stable/modules/feature_extraction.html#tfidf-term-weighting) pour tous les vers dans tous les textes du corpus.
4. Choisir une paire de mots (_femme_ et _homme_, par exemple) pour définir une analogie. La paire permettra la modification d'un vers par le remplacement de tous les mots du vers selon l'analogie (le _roi_ est à l'_homme_ ce que la **_reine_** est à la _femme_).
5. Sélectionner un vers quelconque du corpus.
6. Modifier le vers par des substitutions de mots basées sur l'analogie définie.
7. Construire un vecteur tf-idf pour le vers modifié selon la matrice pour tout le corpus.
8. Chercher le vers dans le corpus qui ressemble le plus au vers modifié selon la [similarité cosinus](https://fr.wikipedia.org/wiki/Similarité_cosinus). La disposition des rimes doit suivre le modèle _abba abba ccd eed_ en alternant de rimes masculines et féminines. La module [epitran](https://github.com/dmort27/epitran) est utile pour la translittération des vers en [API](https://fr.wikipedia.org/wiki/Alphabet_phonétique_international), ce qui assure des rimes correctes.
9. Retourner à l'étape 6 avec le vers cherché et continuer jusqu'à ce que le poème généré soit composé de 14 vers.

Après chaque vers on trouvera une référence au vers original dans le corpus du [Théâtre Classique](http://www.theatre-classique.fr).

## Setup

Here is how you set up the web application:

1. Create a directory and create subdirectories `lib` and `Fievre`. Install this repo as a subdirectory as well.
2. Change directories to the repo.
3. Run `scrapeTheatreClassique.py`. This will download the files for plays from the  [Théâtre Classique](http://www.theatre-classique.fr) website and place them in the directory `../Fievre`.
4. Create a MySQL database by importing `songenapp.sql`. You will need to create two users in MySQL, one to build the database (with `INSERT` and `SELECT` privileges) and one for the web server to access the database (with `SELECT` privileges). You can create these accounts by looking at the parameters set in `buildCorpus.py` and `makeSonnet.py`.
5. Run `build.Corpus.py`, which inserts all alexandrines from verse plays in `../Fievre` into the `corpus` database along with their IPA transliterations. There are formatting errors in the source data downloaded in `../Fievre`. These errors are easy to fix when this script throws an exception: just edit the source data and restart.
6. Run `buildVectorSpace.py`. This will build the word embedding model and save it as `../lib/Fievre_model`. It will also build the dictionary file `../lib/pos_dict.pkl`.
7. The web application `makeSonnet.py` can now be deployed. I recommend [Gunicorn](https://gunicorn.org) for deployment:
```
gunicorn -b localhost:5000 -w 4 -t 120 --preload makeSonnet:app
```
When the server starts up it will first load the word embedding model and vectorize all the verses in the database. This takes a while (about a minute on my 3-year-old MacBook Pro).
