#!/usr/bin/env python3
"""
Copyright (c) 2020 Mark Wolff <wolff.mark.b@gmail.com>

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and
this notice are preserved. This file is offered as-is, without any warranty.
"""

import sys
import re
import os
import epitran
import warnings
import xml.etree.ElementTree as ET
import mysql.connector
import io
from config import vowels, epi

sourcedir = '/media/psf/Home/Research/2019 SonGen/CorpusSonetosSigloDeOro'

mydb = mysql.connector.connect(
  host="localhost",
  user="songenappmaker",
  passwd="make_songenapp",
  database="songen",
  charset='utf8',
  use_unicode=True
)

mycursor = mydb.cursor()
mycursor.execute('SET NAMES UTF8;')

### BEGIN functions and classes
def add2corpus(string, ln):
    s = re.sub('\-+', '-', string)
    s = re.sub('\s*[\.,:;\'\"\u00AB\u00BB\?\¿\!\¡\(\)]+', '', s)
    s = re.sub('\W*$', '', s)
    s = re.sub('^\W*', '', s)

    return [ str(ln), string, epi.transliterate(s) ]

def readFile(fname):
    corpus = list()
    with io.open(fname, mode='r') as myfile:
        string = myfile.read()
    root = ET.fromstring(string)
    author = root.find('.//{http://www.tei-c.org/ns/1.0}sourceDesc/{http://www.tei-c.org/ns/1.0}bibl/{http://www.tei-c.org/ns/1.0}author').text
#    node = root.find('.//text/body/head')
#    title = node.title
    title = root.find('.//{http://www.tei-c.org/ns/1.0}text/{http://www.tei-c.org/ns/1.0}body/{http://www.tei-c.org/ns/1.0}head/{http://www.tei-c.org/ns/1.0}title').text

    string = list()
    ln = ''
    for line in root.findall('.//{http://www.tei-c.org/ns/1.0}l'):
        verse = line.text
        try:
            id = line.attrib['n']
        except:
            raise ValueError('Verse: ' + verse)
        if id == ln or ln == '':
            string.append(verse)
        else:
            s = ' '.join(string)
            if re.match('\S', s):
                corpus.append(add2corpus(s, ln))
            string = [verse]
        ln = id
    s = ' '.join(string)
    if re.match('\S', s):
        corpus.append(add2corpus(s, ln))
    return author, title, corpus

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
##### END functions and classes

sqlqm = 'SELECT id FROM espagnol_metadata WHERE author = %s AND title = %s AND file = %s'
sqlim = 'INSERT INTO espagnol_metadata (author, title, file) VALUES (%s,%s,%s)'
sqlc = 'INSERT INTO espagnol (meta_id,ln,verse,ipa) VALUES (%s,%s,%s,%s)'

for dname in os.listdir(sourcedir):
    if dname in [ 'GuiaAnotacionMetrica.pdf', 'README_esp.md', 'README.md']:
        continue
    for fname in os.listdir(os.path.join(sourcedir, dname)):
        if fname.endswith('xml'):
            eprint('Loading ' + fname)
            author, title, corpus = readFile(os.path.join(sourcedir, dname, fname))
            if not title:
                title = corpus[0][1]
            mycursor.execute(sqlqm, [author, title, fname])
            meta_id = int()
            meta = mycursor.fetchone()
            if not meta:
                mycursor.execute(sqlim, [author, title, fname])
                meta_id = mycursor.lastrowid
            else:
                meta_id = meta[0]
            for datum in corpus:
                mycursor.execute(sqlc, [meta_id] + datum)
            mydb.commit()
mycursor.close()
mydb.close()
eprint('Success!')
