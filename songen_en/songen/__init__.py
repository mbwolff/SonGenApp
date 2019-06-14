#!/usr/bin/env python3
"""
Copyright (c) 2019 Mark Wolff <wolff.mark.b@gmail.com>

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and
this notice are preserved. This file is offered as-is, without any warranty.
"""

from flask import Flask, render_template, request, redirect, url_for, session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import string
import pickle
from .treetagger import TreeTagger
import epitran
import gensim
import random
import numpy
import scipy
import sys
import mysql.connector
from datetime import datetime
from .config import secret_key, model_file, number_of_options, no_phonemes, no_verses, tagdir, epi, IPAV, vowels
from .utils import eprint, connectMySQL

app = Flask(__name__)
if __name__ == "__main__":
    app.run()
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = secret_key

print('{timestamp} -- start loading model file'.format(timestamp=datetime.utcnow().isoformat()))
model = gensim.models.Word2Vec.load(model_file)

print('{timestamp} -- start loading corpus from MySQL'.format(timestamp=datetime.utcnow().isoformat()))
corpus = list()
cnx = connectMySQL()
cursor = cnx.cursor()
query = ('SELECT id, gid, verse, ipa FROM english')
cursor.execute(query)
for (id, gid, verse, ipa) in cursor:
    corpus.append( (id, gid, verse, ipa) )
cursor.close()
cnx.close()
eprint('Size of corpus: ' + str(len(corpus)))

print('{timestamp} -- start loading vectorizer'.format(timestamp=datetime.utcnow().isoformat()))
vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    token_pattern=r'\b\w+\b',
    min_df=1)
vectorized_corpus = vectorizer.fit_transform([vers[2] for vers in corpus])

print('{timestamp} -- everything is loaded'.format(timestamp=datetime.utcnow().isoformat()))

@app.after_request
def apply_caching(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/start', methods=['GET', 'POST'])
def start():
    session['verses'] = list()
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
            revise = '0'
            if 'revise' in request.form:
                revise = request.form['revise']
            chosen = '0'
            if 'chosen' in request.form:
                chosen = request.form['chosen']
            return make_the_sonnet(request.form['pos'], request.form['neg'], chosen, revise, request.form['last_verse'])
        else:
            return 'Error'
    else:
        return show_the_form(error)

@app.route('/again', methods=['GET', 'POST'])
def again():
    error = None
    return redirect(url_for('start'), code=302)

def select_a_verse(string):
    options = list()
    cnx = connectMySQL()
    cursor = cnx.cursor()
    query = ('SELECT id, verse FROM english WHERE verse LIKE %s ORDER BY rand() LIMIT 50')
    cursor.execute(query, ('%' + string + '%',))
    for (id, verse) in cursor:
        options.append( (id, verse) )
    cursor.close()
    cnx.close()
    return render_template('setParams.html', options=options)

def make_the_sonnet(pos, neg, chosen, revise, last_verse):
    verses = list()
    if 'verses' in session:
        verses = session['verses']
    rime = None
    line = len(verses)
    eprint('Line: ' + str(line))
    options = list()
    used_verses = [ v[5] for v in verses ]
    indices = list()
    vers = list()
    chosen = int(chosen)
    message = 0
    modified = False
    modtitle = ''
    if revise != '0':
        for i in range(line):
            if verses[i][5] == int(revise):
                vers = grabVerse(verses[i][5])
                vers[2] = verses[i][0]
                vers[3] = transliterate(vers[2])
                modtitle = verses[i][3]
                eprint('Revise vers:')
                eprint(vers)
                verses = verses[:i]
                if len(verses) > 0:
                    verses[-1][6] = fixRime(i, verses[-1][6])
                used_verses = [ v[5] for v in verses ]
                line = i
                break

    elif bool(verses) and last_verse != verses[-1][0]:
        eprint('Revising...')
        ipa = transliterate(last_verse)
        rime = verses[-1][6]
        v = verses.pop()
        eprint('The verse!')
        eprint(v)
#        vers = [ v[3], v[1], v[2], v[0], ipa ]
        vers = grabVerse(v[5])
        line = len(verses)
        eprint('Before goodverse')
        bv = goodVerse(last_verse, ipa, line, v[6], v[0], vers[3])
        # def goodVerse(verse, ipa, line, r, orig_verse, orig_ipa):

        if bv:
#            vers[4] = re.sub('\u0259\s*$', ' ', transliterate(v[0]))
#            if len(verses) > 0:
#                verses[-1][5] = fixRime(line, verses[-1][5])
            message = bv
        elif not message:
            vers[2] = last_verse
            vers[3] = ipa
            if len(verses) > 0:
                verses[-1][6] = fixRime(line, verses[-1][6])
            modified = True

    elif bool(verses) and chosen == 0 and last_verse == verses[-1][0]:
        vers = grabVerse(verses[-1][5])
        modtitle = verses[-1][3]
        verses.pop()
        if len(verses) > 0:
            verses[-1][6] = fixRime(len(verses), verses[-1][6])
        used_verses = [ v[5] for v in verses ]
        line = len(verses)
    else:
        vers = grabVerse(chosen)

    if line == 0:
        rime = list()
        rime = addNewRime(rime, getRhyme(vers[3])[-no_phonemes:])
        rime = addLW2rime(0, vers[2], rime)
        indices = new_rhyme(rime)
    else:
        rime = verses[-1][6]
        if line == 1:
            rime = addNewRime(rime, getRhyme(vers[3])[-no_phonemes:])
            rime = addLW2rime(1, vers[2], rime)
            indices = check_verse(1, rime)
        elif line == 2:
            rime = addLW2rime(1, vers[2], rime)
            indices = check_verse(0, rime)
        elif line == 3:
            rime = addLW2rime(0, vers[2], rime)
            indices = check_verse(0, rime)
        elif line == 4:
            rime = addLW2rime(0, vers[2], rime)
            indices = check_verse(1, rime)
        elif line == 5:
            rime = addLW2rime(1, vers[2], rime)
            indices = check_verse(1, rime)
        elif line == 6:
            rime = addLW2rime(1, vers[2], rime)
            indices = check_verse(0, rime)
        elif line == 7:
            rime = addLW2rime(0, vers[2], rime)
            indices = new_rhyme(rime)
        elif line == 8:
            rime = addNewRime(rime, getRhyme(vers[3])[-no_phonemes:])
            rime = addLW2rime(2, vers[2], rime)
            indices = check_verse(2, rime)
        elif line == 9:
            rime = addLW2rime(2, vers[2], rime)
            indices = new_rhyme(rime)
        elif line == 10:
            rime = addNewRime(rime, getRhyme(vers[3])[-no_phonemes:])
            rime = addLW2rime(3, vers[2], rime)
            indices = new_rhyme(rime)
        elif line == 11:
            rime = addNewRime(rime, getRhyme(vers[3])[-no_phonemes:])
            rime = addLW2rime(4, vers[2], rime)
            indices = check_verse(4, rime)
        elif line == 12:
            rime = addLW2rime(4, vers[2], rime)
            indices = check_verse(3, rime)
        elif line == 13:
            rime = addLW2rime(3, vers[2], rime)

    author, title = getMetadata(vers[1])
    if modtitle:
        title = modtitle
    if modified and not re.search('[modified]\s*$', title):
        title = title + ' [modified]'
#    if modtitle:
#        title = modtitle
#    elif modified:
#        title = title + ' [modified]'
    tv = transform_verse(vers[2], pos, neg)
    vectorized_tv = vectorizer.transform([tv])
    if vers[0] != 0:
        used_verses.append(vers[0])
    verses.append([ vers[2], vers[1], author, title, tv, vers[0], rime, pos, neg ])
    session['verses'] = verses
    if len(indices) > 0:
        options = getOptions(indices, vectorized_tv, vectorized_corpus, used_verses)

    eprint('Verse:')
    eprint(verses[-1])
    return render_template('sonnet.html', pos=pos, neg=neg, verses=verses, options=options, message=message)

def getRhyme(ipa):
    rhyme = re.sub('\W+', '', ipa)
    return rhyme

def transform_verse(assertion, pos, neg):
    new_words = []
    for w in tag(assertion):
        try:
            hits = []
            psw = w[1]
            for item in model.wv.most_similar(positive=[pos] + [w[2]], negative=[neg], topn=number_of_options):
                hits.append(item[0])
            if len(hits) > 0:
                new_words.append(hits[0])
            else:
                new_words.append(w[0].lower())
        except:
            new_words.append(w[0].lower())
    response = ' '.join(new_words)
    return response

def displayVerse(indices, vectorized_tv, vectorized_corpus, used_verses):
    print('{timestamp} -- trying to display verse'.format(timestamp=datetime.utcnow().isoformat()))
    vector_similarity = cosine_similarity(vectorized_tv, vectorized_corpus)
    vectors = list(vector_similarity.argsort()[::-1][0])
    matches = list()
    stop = random.randint(1,10)
    count = 0
    match = 0
    previous = list()
    for index in vectors:
        if count == stop:
            return grabVerse(match), match
        index = int(index)
        if (index+1 in indices) and (index+1 not in used_verses):
            match = index + 1
            previous.append(match)
            count = count + 1
            eprint('Count displayVerse: ' + str(count))
    if len(previous) > 1:
        match = previous[-1]
        return grabVerse(match)
    else:
        return ( -1, -1, '[Could not find a verse that matches criteria and completes sonnet]', 0 )

def getOptions(indices, vectorized_tv, vectorized_corpus, used_verses):
    print('{timestamp} -- getting options for next verse'.format(timestamp=datetime.utcnow().isoformat()))
    vector_similarity = cosine_similarity(vectorized_tv, vectorized_corpus)
    vectors = list(vector_similarity.argsort()[::-1][0])
    count = 0
    matches = list()
    for index in vectors:
        if count == no_verses:
            return matches
        index = int(index)
        if (index+1 in indices) and (index+1 not in used_verses):
            vers = grabVerse(index+1)
            matches.append( (vers[0], vers[2]) )
            count = count + 1
    return matches

def new_rhyme(r):
    global no_phonemes
    query = list()
    basequery = 'SELECT id FROM english WHERE '
    if len(r) == 0:
        basequery = basequery + '1'
    for i in range(len(r)):
        query.append(('ipa NOT REGEXP %s', str(r[i][0]) + '[[:space:][:punct:]]*$'))
    sql = list()
    data = list()
    for q in query:
        sql.append(q[0])
        data.append(q[1])
    qstring = (basequery + ' AND '.join(sql))
    cnx = connectMySQL()
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
    basequery = 'SELECT id FROM english WHERE '
    query.append(('ipa REGEXP %s', r[index][0] + '[[:space:]]*$'))
    for w in r[index][1]:
        query.append(('LOWER(verse) NOT REGEXP %s', w + '[[:space:][:punct:]]*$'))
    sql = list()
    data = list()
    for q in query:
        sql.append(q[0])
        data.append(q[1])
    qstring = (basequery + ' AND '.join(sql))
    cnx = connectMySQL()
    cursor = cnx.cursor()
    cursor.execute(qstring, tuple(data))
    indices = list()
    for (id) in cursor:
        indices.append(int(id[0]))
    cursor.close()
    cnx.close()
    return indices

def addNewRime(r, sound):
    r.append([ sound, [] ])
    return r

def addLW2rime(i,v,r):
    try:
        lw = re.sub(r'[^\w]+$', '', v)
        lw = lw.lower().split().pop()
        eprint('LW: ' + lw)
    except:
        lw = 'NONE'
        eprint('v:')
        for x in v:
            eprint(x)
        eprint('r:')
        for x in r:
            eprint(x)
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
    cnx = connectMySQL()
    cursor = cnx.cursor()
    query = ('SELECT * FROM english')
    cursor.execute(query)
    for (id, gid, verse, ipa) in cursor:
        corpus.append( (id, gid, verse, ipa) )
    cursor.close()
    cnx.close()
    return corpus

def getVectorizedCorpus():
    corpus = getCorpus()
    return vectorizer.fit_transform([vers[2] for vers in corpus])

def getIndex(i, corpus):
    for index, d in enumerate(corpus):
        if i == int(d[0]):
            return index
    raise ValueError('Could not find index for id ' + i + ' in corpus')

def grabVerse(i):
    vers = None
    cnx = connectMySQL()
    cursor = cnx.cursor()
    query = ('SELECT id, gid, verse, ipa FROM english WHERE id=%s')
    cursor.execute(query, (str(i),))
    vers = cursor.fetchone()
    cursor.close()
    cnx.close()
    return list(vers)

def getMetadata(gid):
    if gid == 0:
        return 0, 0
    cnx = connectMySQL()
    cursor = cnx.cursor()
    query = ('SELECT Surname, Title FROM english_metadata WHERE Num=%s')
    cursor.execute(query, (str(gid),))
    meta = [ None, None ]
    for (Surname, Title) in cursor:
        meta = [ Surname, Title ]
        break
    cursor.close()
    cnx.close()
    return meta[0], re.sub('\t', ' ', meta[1])

def tag(assertion):
    global tagdir
    tt = TreeTagger(path_to_treetagger=tagdir)
    return tt.tag(assertion)

def transliterate(string):
    global epi
    stripped = re.sub('[^\w\s]+', '', string)
    stripped = re.sub('\s*$', ' ', stripped)
    return epi.transliterate(stripped)[:-1]

def goodVerse(verse, ipa, line, r, orig_verse, orig_ipa):
    message = None
    lvlw = re.sub('\W+$', '', verse).split().pop()
    if lvlw.lower() in r[setRime(line)][1]:
        messgae = 'The last word of "' + verse + '" cannot be repeated.'
        return message
    if len(vowels.findall(ipa)) != 10:
        message = 'Incorrect number of syllables.'
        return message
    elif ipa[-no_phonemes:] != orig_ipa[-no_phonemes:]:
        message = 'The rhyme at the end of "' + verse + '" is incorrect.'
        return message
    return message

def setRime(line):
    n = 0
    if line in [ 1, 2, 5, 6 ]:
        n = 1
    elif line in [ 8, 9 ]:
        n = 2
    elif line in [ 10, 13 ]:
        n = 3
    elif line in [ 11, 12 ]:
        n = 4
    return n

def fixRime(l, r):
    eprint('line = ' + str(l))
    if l in [0, 1, 8, 10, 11]:
        r.pop()
    elif l in [2, 5, 6]:
        r[1][1].pop()
    elif l in [3, 4, 7]:
        r[0][1].pop()
    elif l in [9]:
        r[2][1].pop()
    elif l in [12]:
        r[4][1].pop()
    else: # l in [13]
        r[3][1].pop()
    eprint('new rime')
    eprint(r)
    return r
