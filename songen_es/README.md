# SonGenApp in Spanish
## A sonnet generator
### Based on [this contribution](https://github.com/mbwolff/Classique-inconnu) to [NaNoGenMo 2018](https://github.com/NaNoGenMo/2018)

The code for this project generates sonnets in Spanish using the [Corpus of Spanish Golden-Age Sonnets](https://github.com/bncolorado/CorpusSonetosSigloDeOro) developed by [Navarro-Colorado, Borja; Ribes Lafoz, María, and Sánchez, Noelia](http://www.dlsi.ua.es/~borja/navarro2016_MetricalPatternsBank.pdf) (2015). A functional prototype is available [here](http://markwolff.name/wp/digital-humanities-2/invent-your-own-sonnet-using-analytic-tools-to-synthesize-texts/).

Here's the procedure:

1. Clone the Github [repository](https://github.com/bncolorado/CorpusSonetosSigloDeOro) for the corpus.
2. Make a vector space for all words in the corpus using [Gensim's Word2Vec module](https://radimrehurek.com/gensim/models/word2vec.html). The words are lemmatized using [TreeTagger](https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/) to simplify the vector space.
3. Build a [tf-idf matrix](https://scikit-learn.org/stable/modules/feature_extraction.html#tfidf-term-weighting) for all the verses in the corpus.
4. Choose a pair of words to define an analogy (_mujer_ and _hombre_, for instance). The pair will enable a modification of a verse by replacing words according to the analogy (_king_ is to _man_ as **_queen_** is to _woman_).
5. Select a verse from the corpus.
6. Modify the verse with word substitutions based on the vector space.
7. Construct a tf-idf vector for the modified verse based on the matrix for the whole corpus.
8. Find a verse in the corpus that is most similar to the modified verse using cosine similarity. The poem's rhyming scheme should follow the pattern _abba abba ccd eed_. The [epitran](https://github.com/mbwolff/epitran) module is useful for transliterating text into IPA and finding verses that rhyme properly.
9. Return to step 6 with the selected verse and continue until the generated text contains 14 verses.

At the end of each verse is a reference to its source text, which can be referenced in the [repository](https://github.com/bncolorado/CorpusSonetosSigloDeOro). If you move the pointer over a verse, the modified version will appear along with the words used to define the analogy.

## Setup

1. Create the subdirectory `lib` in the `songen_es` directory.
2. Download the files for the poetry corpus and save them in the `songen_es` directory.
3. Create a MySQL database with `songen.sql` (in the parent directory of `songen_es`). You will need to create two users in MySQL, one to build the database (with `INSERT` and `SELECT` privileges) and one for the web server to access the database (with `SELECT` privileges). You can create these accounts by looking at the parameters set in `buildCorpus.py` and `makeSonnet.py`.
4. Run `buildCorpus.py`, which inserts all verses in the corpus into the `espagnol` database table along with their IPA transliterations. The script also builds the `espagnol_metadata` table.
5. Run `buildVectorSpace.py`. This will build the word embedding model and save it as `lib/Sonetos_model`.
6. The web application `makeSonnet.py` can now be deployed. I recommend [Gunicorn](https://gunicorn.org) for deployment. Set `songen_es` as the active directory and run the following:
```
gunicorn -b localhost:5001 -w 4 -t 120 --preload songen:app
```
When the server starts up it will first load the word embedding model and vectorize all the verses in the database. This takes a while (less than a minute on my 3-year-old MacBook Pro).
