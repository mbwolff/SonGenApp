#!/usr/bin/env python3
"""
Copyright (c) 2019 Mark Wolff <wolff.mark.b@gmail.com>

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and
this notice are preserved. This file is offered as-is, without any warranty.
"""
import sys
import re
import pickle
#import treetaggerwrapper
from .treetagger import TreeTagger
import mysql.connector
from config import tagdir
from utils import tag, eprint

picklefile = '../tagSet.pkl'

mydb = mysql.connector.connect(
  host="localhost",
  user="songenappmaker",
  passwd="make_songenapp",
  database="songen",
  charset='utf8',
  use_unicode=True
)

tag_forms = set()

mycursor1 = mydb.cursor()
query1 = 'SELECT id, verse FROM english'
mycursor1.execute(query1)
rows = mycursor1.fetchall()
#mydb.commit()
for (id, verse) in rows:
    mycursor2 = mydb.cursor()
    sent = list()
    for t in tag(verse):
#    for t in tagger.tag_text(verse):
#        t = re.split('\t', t)
        if len(t) < 3:
            continue
        elif t[1] == 'SENT':
            continue
        else:
            sent.append(t[1])
    tags = ' '.join(sent)
    tags = re.sub('^\W+', '', tags)
    tags = re.sub('\W+$', '', tags)
    tags = re.sub(' \W+ ', ' ', tags)
    query2 = 'UPDATE english SET tags = %s WHERE id = %s'
    vals2 = (tags, id)
    tag_forms.add(tags)
    mycursor2.execute(query2, vals2)
    mydb.commit()
    mycursor2.close()
    eprint('Added tags for ' + str(id))
mycursor1.close()
mydb.close()

eprint('There are ' + str(len(tag_forms)) + ' tag forms')
pf = open(picklefile, 'wb')
pickle.dump(tag_forms, pf)
pf.close()
eprint('Success!')
