#!/usr/bin/env python3
"""
Copyright (c) 2019 Mark Wolff <wolff.mark.b@gmail.com>

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and
this notice are preserved. This file is offered as-is, without any warranty.
"""

from flask import Flask, render_template, request, redirect, url_for
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import pickle
import spacy
import gensim
import random
import numpy
import scipy
import sys
import mysql.connector
from datetime import datetime

app = Flask(__name__)
if __name__ == "__main__":
    app.run()

model_file = '../lib/Fievre_model'
pkl_dict = '../lib/pos_dict.pkl'
#VectorizedCorpusFile = '../lib/VectorizedCorpus.pkl'
#VectorizerFile = '../lib/Vectorizer.pkl'
number_of_options = 100
loop_max = 50
no_phonemes = 3

host = 'localhost'
mysql_user = 'songenappuser'
mysql_passwd = 'use_songenapp'
database = 'songenapp'

print('{timestamp} -- start loading pickle file'.format(timestamp=datetime.utcnow().isoformat()))
model = gensim.models.Word2Vec.load(model_file)
pickleFile = open(pkl_dict, 'rb')
posd = pickle.load(pickleFile)
nlp = spacy.load('fr_core_news_sm')

print('{timestamp} -- start loading corpus from MySQL'.format(timestamp=datetime.utcnow().isoformat()))
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

print('{timestamp} -- start loading vectorizer'.format(timestamp=datetime.utcnow().isoformat()))
vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    token_pattern=r'\b\w+\b',
    min_df=1)
vectorized_corpus = vectorizer.fit_transform([vers[3] for vers in corpus])

print('{timestamp} -- everything is loaded'.format(timestamp=datetime.utcnow().isoformat()))
#raise ValueError('Check corpus and vecotrized corpus')
@app.after_request
def apply_caching(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/start', methods=['GET', 'POST'])
def start():
    error = None
    return show_the_form(error)

def show_the_form(error):
    return render_template('search4Verses.html')

@app.route('/getVerses', methods=['GET', 'POST'])
def getVerses():
    error = None
    if request.method == 'POST':
        if 'string' in request.form:
            return select_a_verse(request.form['string'])
        else:
            return 'Error'
    else:
        return show_the_form(error)

@app.route('/makeSonnet', methods=['GET', 'POST'])
def makeSonnet():
    error = None
    if request.method == 'POST':
        if 'pos' in request.form:
            return make_the_sonnet(request.form['pos'], request.form['neg'], request.form['verse'])
        else:
            return 'Error'
    else:
        return show_the_form(error)

@app.route('/again', methods=['GET', 'POST'])
def again():
    error = None
    return redirect(url_for('start'), code=302)

def select_a_verse(string):
    verses = list()
    cnx = mysql.connector.connect(
      host=host,
      user=mysql_user,
      passwd=mysql_passwd,
      database=database,
      charset='utf8',
      use_unicode=True
    )
    cursor = cnx.cursor()
    query = ('SELECT id, verse FROM corpus WHERE verse LIKE %s ORDER BY rand() LIMIT 50')
    cursor.execute(query, ('%' + string + '%',))
    for (id, verse) in cursor:
        verses.append( (id, verse) )
    cursor.close()
    cnx.close()
    return render_template('setParams.html', verses=verses)

def make_the_sonnet(pos, neg, index):
    index = int(index)
    global no_phonemes
    used_verses = list()
    vers = grabVerse(index)
    initial_index = index
    line = 0
    rime = list()
    tv = ''
    verses = list()
#    vectorized_corpus = g_vectorized_corpus
    while line < 14:
        if line == 0: # first verse
            gender = False
            if re.search('e\W*$', vers[3]):
                gender = True
            rime.append([ getRhyme(vers[4])[-no_phonemes:], [], gender ])
            rime = addLW2rime(0, vers, rime)
        else:
            tv = transform_verse(vers[3], pos, neg)
            vectorized_tv = vectorizer.transform([tv])
            if line in { 3, 4, 7 }:
                indices = check_verse(0, rime)
                vers, index = displayVerse(indices, vectorized_tv, vectorized_corpus, used_verses)
                rime = addLW2rime(0, vers, rime)
            elif line in { 1, 2, 5, 6 }:
                if line == 1:
                    indices = new_rhyme(1, rime)
                    vers, index = displayVerse(indices, vectorized_tv, vectorized_corpus, used_verses)
                    rime = addNewRime(rime, getRhyme(vers[4])[-no_phonemes:])
                else:
                    indices = check_verse(1, rime)
                    vers, index = displayVerse(indices, vectorized_tv, vectorized_corpus, used_verses)
                rime = addLW2rime(1, vers, rime)
            elif line in { 8, 9 }:
                if line == 8:
                    indices = new_rhyme(2, rime)
                    vers, index = displayVerse(indices, vectorized_tv, vectorized_corpus, used_verses)
                    rime = addNewRime(rime, getRhyme(vers[4])[-no_phonemes:])
                else:
                    indices = check_verse(2, rime)
                    vers, index = displayVerse(indices, vectorized_tv, vectorized_corpus, used_verses)
                rime = addLW2rime(2, vers, rime)
            elif line in { 10, 13 }:
                if line == 10:
                    indices = new_rhyme(3, rime)
                    vers, index = displayVerse(indices, vectorized_tv, vectorized_corpus, used_verses)
                    rime = addNewRime(rime, getRhyme(vers[4])[-no_phonemes:])
                else:
                    indices = check_verse(3, rime)
                    vers, index = displayVerse(indices, vectorized_tv, vectorized_corpus, used_verses)
                rime = addLW2rime(3, vers, rime)
            else: # line in { 11, 12 }:
                if line == 11:
                    indices = new_rhyme(4, rime)
                    vers, index = displayVerse(indices, vectorized_tv, vectorized_corpus, used_verses)
                    rime = addNewRime(rime, getRhyme(vers[4])[-no_phonemes:])
                else:
                    indices = check_verse(4, rime)
                    vers, index = displayVerse(indices, vectorized_tv, vectorized_corpus, used_verses)
                rime = addLW2rime(4, vers, rime)
        line = line + 1
        verses.append([ str(line), vers[3], vers[1], vers[2], tv ])
        if vers[0] == -1:
            return render_template('sonnet.html', pos=pos, neg=neg,
                no_verses_corpus=initial_index, verses=verses)
        else:
            used_verses.append(index)
            print('\'' + vers[3] + '\'')
            print('\'' + vers[4] + '\'')
            print()
    return render_template('sonnet.html', pos=pos, neg=neg,
        no_verses_corpus=initial_index, verses=verses)

def getRhyme(ipa):
    return re.sub('\W*$', '', ipa, flags=re.UNICODE)

def transform_verse(assertion, pos, neg):
    parsed = nlp(assertion)
    new_words = []
    for word in parsed:
        try:
            hits = []
            psw = word.tag_.split('__')[0]
            for item in model.wv.most_similar(positive=[pos] + [word.lemma_.lower()], negative=[neg], topn=number_of_options):
                if posd[item[0]]:
                    psd = next(iter(posd[item[0]])).split('__')[0]
                    hits.append(item[0])
            if len(hits) > 0:
                new_words.append(hits[0])
            else:
                new_words.append(word.text.lower())
        except:
            new_words.append(word.text.lower())
    response = ' '.join(new_words)
    return response

def displayVerse(indices, vectorized_tv, vectorized_corpus, used_verses):
    print('{timestamp} -- trying to display verse'.format(timestamp=datetime.utcnow().isoformat()))
    vector_similarity = cosine_similarity(vectorized_tv, vectorized_corpus)
    for index in list(vector_similarity.argsort()[::-1][0]):
        index = int(index)
        if (index+1 in indices) and (index+1 not in used_verses):
            return grabVerse(index+1), index+1
#    raise ValueError('Could not find a verse that matches criteria.')
    return ( -1, 'NOFILE', 0, '[Could not find a verse that matches criteria and completes sonnet]', '' ), 0

def new_rhyme(index,r):
    global no_phonemes
    gender = not r[index-1][2]
    query = list()
    basequery = 'SELECT id FROM corpus WHERE '
    if gender == False:
        query.append(( 'LOWER(verse) NOT REGEXP %s', 'e[[:space:]]*[[:punct:]]*[[:space:]]*$' ))
    else:
        query.append(( 'LOWER(verse) REGEXP %s', 'e[[:space:]]*[[:punct:]]*[[:space:]]*$' ))
    for i in range(0, index):
        query.append(( 'ipa NOT REGEXP %s', str(r[i][0]) + '[[:space:]]*[[:punct:]]*[[:space:]]*$' ))
    sql = list()
    data = list()
    for q in query:
        sql.append(q[0])
        data.append(q[1])
    qstring = (basequery + ' AND '.join(sql))
#    print(data)
    cnx = mysql.connector.connect(
        host=host,
        user=mysql_user,
        passwd=mysql_passwd,
        database=database,
        charset='utf8',
        use_unicode=True
    )
    cursor = cnx.cursor()
    cursor.execute(qstring, tuple(data))
    indices = list()
    for (id) in cursor:
        indices.append(int(id[0]))
    cursor.close()
    cnx.close()
    return indices

def check_verse(index,r):
    global no_phonemes
    query = list()
    basequery = 'SELECT id FROM corpus WHERE '
    query.append(( 'ipa REGEXP %s', str(r[index][0]) + '[[:space:]]*$' ))
    if r[index][2] == False:
        query.append(( 'LOWER(verse) NOT REGEXP %s', 'e[[:space:]]*[[:punct:]]*[[:space:]]*$' ))
    else:
        query.append(( 'LOWER(verse) REGEXP %s', 'e[[:space:]]*[[:punct:]]*[[:space:]]*$' ))
    for w in r[index][1]:
        query.append(( 'LOWER(verse) NOT REGEXP %s', str(w) + '[[:space:]]*[[:punct:]]*[[:space:]]*$'))
    sql = list()
    data = list()
    for q in query:
        sql.append(q[0])
        data.append(q[1])
    qstring = (basequery + ' AND '.join(sql))
    cnx = mysql.connector.connect(
        host=host,
        user=mysql_user,
        passwd=mysql_passwd,
        database=database,
        charset='utf8',
        use_unicode=True
    )
    cursor = cnx.cursor()
    cursor.execute(qstring, tuple(data))
    indices = list()
    for (id) in cursor:
        indices.append(int(id[0]))
    cursor.close()
    cnx.close()
    return indices

def addNewRime(r, sound):
    gender = not r[-1][2]
    r.append([ sound, [], gender ])
#    print('Sound: ' + sound.encode('utf-8'))
    return r

def addLW2rime(i,v,r):
    lw = re.sub('\W+$', '', v[3], flags=re.UNICODE).lower().split().pop()
#    print('Last word: ' + lw)
    r[i][1].append(lw)
    return r

def getIndex(v, c):
    index = -1
    while index < 0:
        for i in range(0,len(c)):
            if v[0] == c[i][0] and v[1] == c[i][1]:
                index = i
    return index

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return update_wrapper(no_cache, view)

def getCorpus():
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
    return corpus

def getVectorizedCorpus():
    corpus = getCorpus()
    return vectorizer.fit_transform([vers[3] for vers in corpus])

def getIndex(i, corpus):
    for index, d in enumerate(corpus):
        if i == int(d[0]):
            return index
    raise ValueError('Could not find index for id ' + i + ' in corpus')

def grabVerse(i):
    vers = None
    cnx = mysql.connector.connect(
      host=host,
      user=mysql_user,
      passwd=mysql_passwd,
      database=database,
      charset='utf8',
      use_unicode=True
    )
    cursor = cnx.cursor()
    query = ('SELECT id, fname, ln, verse, ipa FROM corpus WHERE id=%s')
    cursor.execute(query, (str(i),))
    for (id, fname, ln, verse, ipa) in cursor:
        vers = ( id, fname, ln, verse, ipa )
        break
    cursor.close()
    cnx.close()
    return vers
