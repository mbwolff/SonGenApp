#!/usr/bin/env python3
"""
Copyright (c) 2018 Mark Wolff <wolff.mark.b@gmail.com>

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and
this notice are preserved. This file is offered as-is, without any warranty.
"""


from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import numpy
import scipy
import sys
import mysql.connector
from datetime import datetime

pickeledVectorizedCorpusFile = '../lib/VectorizedCorpus.pkl'
pickeledVectorizerFile = '../lib/Vectorizer.pkl'

host = 'localhost'
mysql_user = 'songenappuser'
mysql_passwd = 'use_songenapp'
database = 'songenapp'

print('{timestamp} -- started loading corpus file'.format(timestamp=datetime.utcnow().isoformat()))

corpus = list()
cnx = mysql.connector.connect(
  host=host,
  user=mysql_user,
  passwd=mysql_passwd,
  database=database,
  charset='utf8',
  use_unicode=True
)
cursor = cnx.cursor()
query = ('SELECT * FROM corpus')
cursor.execute(query)
for (id, fname, ln, verse, ipa) in cursor:
    corpus.append( (id, fname, ln, verse, ipa) )
cursor.close()
cnx.close()

print('{timestamp} -- started building vectorizer'.format(timestamp=datetime.utcnow().isoformat()))
vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    token_pattern=r'\b\w+\b',
    min_df=1)
vectorized_corpus = vectorizer.fit_transform([vers[3] for vers in corpus])

print('{timestamp} -- started saving vectorizer'.format(timestamp=datetime.utcnow().isoformat()))
pickledVectorizedCorpus = open(pickeledVectorizedCorpusFile, 'wb')
pickle.dump(vectorized_corpus, pickledVectorizedCorpus)
pickledVectorizedCorpus.close()

pickeledVectorizer = open(pickeledVectorizerFile, 'wb')
pickle.dump(vectorizer, pickeledVectorizer)
pickeledVectorizer.close()
print('{timestamp} -- done saving vectorizer'.format(timestamp=datetime.utcnow().isoformat()))
