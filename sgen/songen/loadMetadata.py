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
import warnings
import mysql.connector
import io
import gzip
import json
from gutenbergdammit.ziputils import loadmetadata

source = '../../../SonGenEngApp/gutenberg-dammit-files-v002.zip'

mydb = mysql.connector.connect(
  host="localhost",
  user="songenappmaker",
  passwd="make_songenapp",
  database="songen",
  charset='utf8',
  use_unicode=True
)

mycursor = mydb.cursor()
keys = ['Author', 'Author Birth', 'Author Death', 'Author Given', 'Author Surname',
'Copyright Status', 'Language', 'LoC Class', 'Num', 'Subject', 'Title']

def db_insert(corpus):
    sql = u'INSERT INTO english_metadata (Author, Birth, Death, Given, Surname, Copyright, Language, LoC, Num, Subject, Title) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    for datum in corpus:
#        try:
        mycursor.execute(sql, datum)
#        except:
#            raise ValueError('Problem: ' + ' '.join(list(datum)))
    mydb.commit()

metadata = loadmetadata(source)

for i in metadata:
    d = list()
    for k in keys:
        i[k] = i.get(k) or 'None'
        if type(i[k]) is list:
            i[k] = re.sub('^\s*\[\'*', '', str(i[k]))
            i[k] = re.sub('\'*\]\s*$', '', str(i[k]))
            i[k] = re.sub('\', \'', ' ', str(i[k]))
#            for n in i[k]:
#                n = str(n)
#            i[k] = ' '.join(i[k])
        d.append(i[k])


    db_insert( [ tuple(d) ] )
