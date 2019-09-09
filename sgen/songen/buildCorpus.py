#!/usr/bin/env python3
"""
Copyright (c) 2019 Mark Wolff <wolff.mark.b@gmail.com>

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and
this notice are preserved. This file is offered as-is, without any warranty.
"""

import sys
import re
import os
import epitran
#import subprocess
import warnings
#import xml.etree.ElementTree as ET
import mysql.connector
import io
import gzip
import json
from config import IPAV, vowels, epi
from utils import eprint, connectMySQL

archive = '../gutenberg-poetry-v001.ndjson.gz'

mydb = connectMySQL()

mycursor = mydb.cursor()
mycursor.execute('SET NAMES UTF8;')

def add2corpus(corpus, string, gid):
    stripped = re.sub('[^\w\s]+', '', string)
    stripped = re.sub('\s*$', ' ', stripped)

    ipa = epi.transliterate(stripped)
    if len(vowels.findall(ipa)) == 10:
        l = ( gid, string, ipa )
        corpus.append(l)
    return corpus

def db_insert(corpus):
    sql = u'INSERT INTO corpus (gid,verse,ipa) VALUES (%s,%s,%s)'
    for datum in corpus:
        try:
            mycursor.execute(sql, datum)
        except:
            raise ValueError('File: ' + datum[0] + '; verse: ' + datum[2])
    mydb.commit()

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
##### END functions and classes

corpus = list()
ln = 0
gid = 0
for line in gzip.open(archive):
    line = json.loads(line.strip())
    if gid != line['gid']:
        gid = line['gid']
        eprint('Doc ' + gid)
#    if len(line['s']) <= 60:
    c1 = len(corpus)
    corpus = add2corpus(corpus, line['s'], line['gid'])
    c2 = len(corpus)
    if c2 > c1:
        ln = ln + 1
        if ln % 100 == 0:
            db_insert(corpus)
            eprint(str(ln) + ' lines so far')
            corpus = list()
#    eprint(line['s'])
eprint(str(ln) + ' total lines')
db_insert(corpus)
mycursor.close()
mydb.close()
eprint('Success!')
