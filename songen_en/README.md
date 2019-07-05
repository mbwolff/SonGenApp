# SonGenApp in English
## A sonnet generator
### Based on [this contribution](https://github.com/mbwolff/Classique-inconnu) to [NaNoGenMo 2018](https://github.com/NaNoGenMo/2018)

The code for this project generates sonnets in English with [pentameters](https://literarydevices.net/pentameter/) using the [Gutenberg Poetry Corpus](https://github.com/aparrish/gutenberg-poetry-corpus) developed by [Allison Parrish](https://www.decontextualize.com/). A functional prototype is available [here](http://markwolff.name/wp/digital-humanities-2/invent-your-own-sonnet-using-analytic-tools-to-synthesize-texts/).

Here's the procedure:

1. Download the poetry corpus and all of [Gutenberg, dammit](https://github.com/aparrish/gutenberg-dammit).
2. Make a vector space for all words in the corpus using [Gensim's Word2Vec module](https://radimrehurek.com/gensim/models/word2vec.html). The words are lemmatized using [TreeTagger](https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/) to simplify the vector space.
3. Build a [tf-idf matrix](https://scikit-learn.org/stable/modules/feature_extraction.html#tfidf-term-weighting) for all the pentameters in the corpus.
4. Choose a pair of words to define an analogy (_woman_ and _man_, for instance). The pair will enable a modification of a verse by replacing words according to the analogy (_king_ is to _man_ as **_queen_** is to _woman_).
5. Select a verse from the corpus.
6. Modify the verse with word substitutions based on the vector space.
7. Construct a tf-idf vector for the modified verse based on the matrix for the whole corpus.
8. Find a verse in the corpus that is most similar to the modified verse using cosine similarity. The poem's rhyming scheme should follow the pattern _abba abba ccd eed_. The [epitran](https://github.com/mbwolff/epitran) module is useful for transliterating text into IPA and finding verses that rhyme properly.
9. Return to step 6 with the selected verse and continue until the generated text contains 14 verses.

At the end of each verse is a reference to its source text, which can be referenced in the [Project Gutenberg](http://www.gutenberg.org). If you move the pointer over a verse, the modified version will appear along with the words used to define the analogy.

## Setup

1. Create the subdirectory `lib` in the `songen_en` directory.
2. Download the files for the poetry corpus and Gutenberg, dammit save them in the `songen_en` directory.
3. Create a MySQL database with `songen.sql` (in the parent directory of `songen_en`). You will need to create two users in MySQL, one to build the database (with `INSERT` and `SELECT` privileges) and one for the web server to access the database (with `SELECT` privileges). You can create these accounts by looking at the parameters set in `buildCorpus.py` and `makeSonnet.py`.
4. Run `buildCorpus.py`, which inserts all pentameters in the poetry corpus into the `english` database table along with their IPA transliterations.
5. Run `buildVectorSpace.py`. This will build the word embedding model and save it as `lib/gutenberg_model`.
6. Run the `loadMetadata.py` to populate the `english_metadata` table.
7. The web application `makeSonnet.py` can now be deployed. I recommend [Gunicorn](https://gunicorn.org) for deployment. Set `songen_en` as the active directory and run the following:
```
gunicorn -b localhost:5001 -w 4 -t 120 --preload songen:app
```
When the server starts up it will first load the word embedding model and vectorize all the verses in the database. This takes a while (less than a minute on my 3-year-old MacBook Pro).
