# SonGenApp français
## A French sonnet generator
### Based on [this contribution](https://github.com/mbwolff/Classique-inconnu) to [NaNoGenMo 2018](https://github.com/NaNoGenMo/2018)

The code for this project generates sonnets in French with [alexandrines](https://en.wikipedia.org/wiki/Alexandrine) using the [Théâtre Classique](http://www.theatre-classique.fr)'s online collection of French plays from the sixteenth to the nineteenth centuries. A functional prototype is available [here](http://markwolff.name/wp/digital-humanities-2/invent-your-own-sonnet-using-analytic-tools-to-synthesize-texts/).

Here's the procedure:

1. Scrape the links for all the XML files of the plays from [this page](http://www.theatre-classique.fr/pages/programmes/PageEdition.php) and then download them to build a corpus.
2. Make a vector space for all words in the corpus using [Gensim's Word2Vec module](https://radimrehurek.com/gensim/models/word2vec.html). The words are lemmatized using [Spacy](https://spacy.io/) to simplify the vector space.
3. Build a [tf-idf matrix](https://scikit-learn.org/stable/modules/feature_extraction.html#tfidf-term-weighting) for all the verses in all the plays in the corpus.
4. Choose a pair of words to define an analogy (_femme_ and _homme_, for instance). The pair will enable a modification of a verse by replacing words according to the analogy (_roi_ is to _homme_ as **_reine_** is to _femme_).
5. Select a verse from the corpus.
6. Modify the verse with word substitutions based on the vector space.
7. Construct a tf-idf vector for the modified verse based on the matrix for the whole corpus.
8. Find a verse in the corpus that is most similar to the modified verse using cosine similarity. The poem's rhyming scheme should follow the pattern _abba abba ccd eed_ where the rhymes alternate between feminine (the last word of the verse ending in a silent _e_) and masculine (the last word ending in some other letter). The [epitran](https://github.com/dmort27/epitran) module is useful for transliterating text into IPA and finding verses that rhyme properly.
9. Return to step 6 with the selected verse and continue until the generated text contains 14 verses.

At the end of each verse is a reference to its source text and line number, which can be referenced in the [Théâtre Classique](http://www.theatre-classique.fr). If you move the pointer over a verse, the modified version will appear along with the words used to define the analogy.

## Setup

1. Create subdirectories `lib` and `Fievre` in the `sgfr` directory.
2. Run `scrapeTheatreClassique.py` (in the `songen` subdirectory). This will download the files for plays from the  [Théâtre Classique](http://www.theatre-classique.fr) website and place them in the directory `Fievre`.
4. Create a MySQL database with `songen.sql` (in the parent directory of `songen_fr`). You will need to create two users in MySQL, one to build the database (with `INSERT` and `SELECT` privileges) and one for the web server to access the database (with `SELECT` privileges). You can create these accounts by looking at the parameters set in `buildCorpus.py` and `config.py`.
5. Run `buildCorpus.py`, which inserts all alexandrines from verse plays in `Fievre` into the `français` database table along with their IPA transliterations. There may be formatting errors in the source data. These errors are easy to fix when the script throws an exception: just edit the source data and restart.
6. Run `buildVectorSpace.py`. This will build the word embedding model and save it as `lib/Fievre_model`.
7. The web application can now be deployed. I recommend [Gunicorn](https://gunicorn.org) for deployment. Set `sgfr` as the active directory and run the following:
```
gunicorn -b localhost:5000 -w 4 -t 120 --preload songen:app
```
When the server starts up it will first load the word embedding model and vectorize all the verses in the database.
