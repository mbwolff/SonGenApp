# SonGenApp
## A French sonnet generator
### Based on [this contribution](https://github.com/mbwolff/Classique-inconnu) to [NaNoGenMo 2018](https://github.com/NaNoGenMo/2018)

The code for this project generates sonnets in French with [Alexandrines](https://en.wikipedia.org/wiki/Alexandrine) using the [Théâtre Classique](http://www.theatre-classique.fr)'s online collection of French plays from the sixteenth to the nineteenth centuries.

Here's the procedure:

1. Scrape the links for all the XML files of the plays from [this page](http://www.theatre-classique.fr/pages/programmes/PageEdition.php) and then download them to build a corpus.
2. Make a vector space for all words in the corpus using [Gensim's Word2Vec module](https://radimrehurek.com/gensim/models/word2vec.html). The words are lemmatized using [SpaCy](https://spacy.io) to simplify the vector space.
3. Build a [tf-idf matrix](https://scikit-learn.org/stable/modules/feature_extraction.html#tfidf-term-weighting) for all the verses in all the plays in the corpus.
4. Choose a pair of words to form the basis of an analogy (_femme_ and _homme_, for instance). The pair will enable a modification of a verse by replacing words according to the analogy (_roi_ is to _homme_ as **_reine_** is to _femme_).
5. Select a random verse from the corpus.
6. Modify the verse with word substitutions based on the vector space.
7. Construct a tf-idf vector for the modified verse based on the matrix for the whole corpus.
8. Find a verse in the corpus that is most similar to the modified verse using cosine similarity. The poem's rhyming scheme should follow the pattern _abba abba ccd eed_ where the rhymes alternate between feminine (the last word of the verse ending in a silent _e_) and masculine (the last word ending in some other letter). The [epitran module](https://github.com/dmort27/epitran) is useful for transliterating text into IPA, although it is imperfect (as its authors acknowledge) because the relationship between word spellings and phonetics in French is complicated.
9. Return to step 6 with the selected verse and continue until the generated text contains 14 verses.

Here is an example of a generated sonnet:

```
1. Que l'amour est déchu de son autorité (CREBILLON_CATILINA.xml:351)
2. Quoi ! Vous feriez cet illustre Molière, (IMBERT_POINSINETMOLIERE.xml:1)
3. Venir sur son tombeau jurer a votre père (CREBILLON_ELECTRE.xml:1102)
4. Le feront adorer de la postérité. (MONTFLEURY_IMPROMPTUCONDE.xml:60)

5. Vous prenez sa défense avec vivacité ! (MARCHADIER_PLAISIR.xml:394)
6. On n'est pas innocent lorsqu'on peut leur déplaire : (CREBILLON_IDOMENEE.xml:60)
7. Je ne puis oublier que leur chef est mon frère. (CORNEILLEP_MORTPOMPEE.xml:1434)
8. Servant aveuglement une Divinité. (TRISTAN_MORTDECHRISPE.xml:1366)

9. Le Sabre de Galas, celui de Jean de Verth. (MARESCHALA_VERITABLECAPITAINEMATAMORE.xml:1172)
10. Je lui donne au souper d'un poignard pour dessert. (TRISTAN_MORTSENEQUE.xml:432)
11. Lesquels sans contourner le rond du voisinage (AURE_DIPNE.xml:243)

12. Voudrait charger sa main de cet horrible emploi ? (CREBILLON_IDOMENEE.xml:1218)
13. Et que sur ce penchant il se fasse une loi... (CORNEILLET_PYRRHUS.xml:35)
14. Comme vous gai, brillant, aimable ; mais volage ; (MARCHADIER_PLAISIR.xml:145)
```

At the end of each verse is a reference to its source text and line number, which can be referenced in the [Théâtre Classique](http://www.theatre-classique.fr).
