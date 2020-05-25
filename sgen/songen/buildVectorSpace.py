#!/usr/bin/env python3
"""
Copyright (c) 2019 Mark Wolff <wolff.mark.b@gmail.com>

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and
this notice are preserved. This file is offered as-is, without any warranty.
"""
import sys
import gzip
import json
import os
import pickle
#import treetaggerwrapper
from treetagger import TreeTagger
import re
import csv
import logging
import gensim
import shutil
import zipfile
from six import iteritems
from config import tagdir
from utils import tag, eprint

# Get the module below and the link for zfile from
# github.com/aparrish/gutenberg-dammit
from gutenbergdammit.ziputils import retrieve_one

# You will need to point this var to where the zipfile is located on your drive.
zfile = '../../../SonGenEngApp/gutenberg-dammit-files-v002.zip'

json_path = 'gutenberg-dammit-files/gutenberg-metadata.json'
path_root = 'gutenberg-dammit-files/'
pickledir = '../gutenberg_pickled'
saved = '../lib/gutenberg_model'

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def getTagged(path):
	pickleFile = open(path, 'rb')
	eprint(path)
	sentences = pickle.load(pickleFile)
	return sentences

class MySentences(object):
    def __init__(self, dirname):
        self.dirname = dirname
    def __iter__(self):
        for fname in os.listdir(self.dirname):
            if fname.endswith('pkl'):
                for sent in getTagged(os.path.join(self.dirname, fname)):
                    yield [ x[2] for x in sent ]

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
######################
#tagger = treetaggerwrapper.TreeTagger(TAGLANG='en', TAGDIR=tagdir)

if not os.path.exists(pickledir):
    os.makedirs(pickledir)

with zipfile.ZipFile(zfile, 'r') as myzip:
	with myzip.open(json_path) as myfile:
		metadata = json.loads(myfile.read())
for i in metadata:
	fn = i['gd-num-padded'] + '.pkl'
	if i['gd-num-padded'] in {'00004', '00050', '00127', '00672', '00744', '00212', '02583'}: # pi, e, phi
		continue
	elif os.path.exists(os.path.join(pickledir, fn)):
		eprint('Already have ' + i['gd-num-padded'])
	elif i['Language'] and i['Language'][0] == 'English':
		eprint('Attempting ' + i['gd-num-padded'])
		text = retrieve_one(zfile, i['gd-path'])
		sentences = list()
		sent = list()
		for t in tag(text):
			if len(t) < 3:
				continue
			sent.append(tuple(t))
			if t[1] == 'SENT':
				sentences.append(sent)
				sent = list()
		if len(sent) > 3:
			sentences.append(sent)
		pickleFile = open(os.path.join(pickledir, fn), 'wb')
		pickle.dump(sentences, pickleFile)
#		eprint('Dumped ' + i['gd-num-padded'])

sentences = MySentences(pickledir) # a memory-friendly iterator
model = gensim.models.Word2Vec(sentences, workers=8)
model.init_sims(replace=True)
model.save(saved)
