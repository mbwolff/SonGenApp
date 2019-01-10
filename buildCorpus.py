#!/usr/bin/env python3
"""
Copyright (c) 2019 Mark Wolff <wolff.mark.b@gmail.com>

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and
this notice are preserved. This file is offered as-is, without any warranty.
"""

from __future__ import print_function
import sys
import re
#import pickle
import os
import epitran
import warnings
import xml.etree.ElementTree as ET
import lxml
#import mysql.connector
import mysql.connector
import io

sourcedir = '../Fievre'
#sourcedir = 'testdata'
#pickeledCorpusFile = os.path.join('lib', 'FievreCorpus.pkl')

epi = epitran.Epitran('fra-Latn')

mydb = mysql.connector.connect(
  host="localhost",
  user="songenappmaker",
  passwd="make_songenapp",
  database="songenapp",
  charset='utf8',
  use_unicode=True
)
#mydb = MySQLdb.connect(
#  host='localhost',
#  user='songenappmaker',
#  passwd='make_songenapp',
#  db='songenapp',
#  charset='utf8',
# use_unicode=True
#)

mycursor = mydb.cursor()
mycursor.execute('SET NAMES UTF8;')

### BEGIN functions and classes
def add2corpus(corpus, string, fname, ln):
    stripped = re.sub(u'[^\w\s]+', '', string, flags=re.UNICODE)
    stripped = re.sub(u'\s*$', ' ', stripped, flags=re.UNICODE)

    ipa = epi.transliterate(stripped)
    if type(string) == type(str()):
        string = string.decode('utf-8')
#    eprint('String: ' + repr(string) + '; ' + string.encode('utf-8'))
    l = (
      unicode(fname),
      unicode(str(ln)),
      string,
      ipa
    )
    corpus.append(l)

def count_vowels(v):
    try:
        s = re.sub('[^\w\s]+', '', v)
        s = re.sub('\s*$', ' ', s)
        ipa = epi.transliterate(s)
        count = len(re.findall(u'[\u0069\u0079\u0268\u0289\u026F\u0075\u0065\u00F8\u0258\u0275\u006F\u0259\u025B\u0153\u025C\u0254\u00E6\u0250\u0061\u0276\u0251\u0252]', ipa))
        return count
    except:
        raise ValueError('Verse: ' + str(v))

def readFile(fname, corpus):
#    with codecs.open(os.path.join(sourcedir, fname), encoding='utf-8') as myfile:
    with io.open(os.path.join(sourcedir, fname), mode='r', encoding='utf-8') as myfile:
#    with open(os.path.join(sourcedir, fname), 'r') as myfile:
        string = myfile.read().encode('utf-8')
#    eprint('Type: ' + str(type(string)))
    root = ET.fromstring(string)

#    with open(os.path.join(sourcedir, fname), 'r') as myfile:
#        tree = ET.parse(myfile)
#    root = tree.getroot()

    node = root.find('.//SourceDesc/type')
    if node is not None and node.text == 'vers':
        string = []
        ln = 1
        for line in root.findall('.//body//l'):
            verse = line.text
#            eprint('Verse: ' + verse)
            if type(verse) is str:
                verse = verse.decode('utf-8')
#            eprint(type(verse))

#####################
            id = int(line.attrib['id'])
            if not verse or count_vowels(verse) < 10 or len(verse) > 128:
                continue
            elif id == ln:
                string.append(verse)
            else:
                s = u' '.join(string)
                if re.match('\S', s):
                    add2corpus(corpus, s, fname, ln)
#                add2corpus(corpus, u' '.join(string), fname, ln)
#                eprint('Type: ' + str(type(u' '.join(string))))
                string = [verse]
                ln = id
#####################
#            add2corpus(corpus, verse, fname, ln)
        s = u' '.join(string)
        if re.match('\S', s):
            add2corpus(corpus, s, fname, ln)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
##### END functions and classes

corpus = list()
for fname in os.listdir(sourcedir):
    if fname.endswith('xml'):
        eprint('Loading ' + fname)
        readFile(fname, corpus)

sql = u'INSERT INTO corpus (fname,ln,verse,ipa) VALUES (%s,%s,%s,%s)'
for datum in corpus:
    try:
        mycursor.execute(sql, datum)
    except:
        raise ValueError('File: ' + datum[0].encode('utf-8') + '; verse: ' + datum[2].encode('utf-8'))
#    mycursor.execute(sql, [ datum[0], datum[1], unicode([datum[2]), datum[3] ])
#    mydb.commit()
#mycursor.executemany(sql, corpus)
#pickledCorpus = open(pickeledCorpusFile, 'wb')
#pickle.dump(corpus, pickledCorpus)
mydb.commit()
eprint('Success!')
mycursor.close()
mydb.close()
