#!/usr/bin/env python3
"""
Copyright (c) 2019 Mark Wolff <wolff.mark.b@gmail.com>

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and
this notice are preserved. This file is offered as-is, without any warranty.
"""

import os
import pickle
#import spacy
#import treetaggerwrapper
from treetagger import TreeTagger
import re
import csv
import logging
import gensim
import shutil
import xml.etree.cElementTree as ET
from six import iteritems
from utils import eprint, tag
from config import tagdir

sourcedir = '../Fievre'

pickledir = '../Fievre_pickled'
saved = os.path.join('../lib', re.sub('pickled$', 'model', pickledir))
#pos_dict = os.path.join('../lib', 'pos_dict.pkl')

### functions and classes
def getTagged(path):
	pickleFile = open(path, 'rb')
	sentences = pickle.load(pickleFile)
	return sentences

class MySentences(object):
	def __init__(self, dirname):
		self.dirname = dirname
	def __iter__(self):
		for fname in os.listdir(self.dirname):
			if fname.endswith('pkl'):
				for sent in getTagged(os.path.join(self.dirname, fname)):
					yield sent

######################
# nlp = spacy.load('fr_core_news_sm')
#tagger = treetaggerwrapper.TreeTagger(TAGLANG='fr', TAGDIR=tagdir)

if not os.path.exists(pickledir):
    os.makedirs(pickledir)

#pd = dict()
num_files = 0
for fname in os.listdir(sourcedir):
	if fname.endswith('xml'):
#		print(fname)
		nfname = re.sub('xml$', 'pkl', fname)
		if os.path.exists(os.path.join(pickledir, nfname)):
			print('Already have ' + nfname)
			continue
		with open(os.path.join(sourcedir, fname), 'rb') as myfile:
#			string = myfile.read().decode('iso-8859-1').encode('utf8')
			string = myfile.read()
		try:
			root = ET.fromstring(string)
		except:
			continue

		node = root.find('.//SourceDesc/type')
		if node is not None and node.text == 'vers':
#		if root.find('.//SourceDesc/type').text == 'vers':
			num_files = num_files + 1
			print(str(num_files) + ' ' + fname)
			string = str()
			work = list()
			ln = 1
			for line in root.findall('.//body//l'):
				verse = str(line.text)
				id = int(line.attrib['id'])
#				print(str(id))
				if id == ln:
					string = string + ' ' + verse
				else:
					work.append(re.sub('^\s+', '', string, flags=re.UNICODE))
					string = verse
					ln = id
			work.append(re.sub('^\s+', '', string, flags=re.UNICODE))
			sections = []
			current_section = ''
			last_chunk = work.pop()
			for chunk in work:
				if len(current_section) + len(chunk) + 1 < 1000000:
				# Spacy requires texts of length no more than 1000000
					current_section = current_section + ' ' + chunk
				else:
					sections.append(current_section)
					current_section = chunk

			current_section = current_section + last_chunk
			sections.append(re.sub('^\s+', '', current_section, flags=re.UNICODE))

			section_counter = 0
			for section in sections:
#				doc = nlp(str(section))
#				parsed = [(w.text, w.tag_, w.lemma_) for w in doc]
				sentences = list()
				sent = list()
				for t in tag(section):
#				for t in tagger.tag_text(section):
#					eprint(t)
#				for token in parsed:
#					text = token[0]
#					pos = token[1]
#					lemma = token[2].lower()
#					t = re.split('\t', t)
					if len(t) < 3:
						continue
#					sent.append(tuple(t))
					sent.append(t[2].lower())
					if t[1] == 'SENT':
						sentences.append(sent)
						sent = list()
				if len(sent) > 3:
					sentences.append(sent)

#					if re.match('PUNCT', pos, flags=re.UNICODE) and re.match(r'[\.\!\?]', text, flags=re.UNICODE):
#						sent.append(lemma)
#						sentences.append(sent)
#						sent = []
#					else:
#						if not re.match('PUNCT', pos, flags=re.UNICODE):
#							lemma = re.sub('^\W+', '', lemma, flags=re.UNICODE)
#							lemma = re.sub('\W+$', '', lemma, flags=re.UNICODE)
#						if re.match('\w', pos, flags=re.UNICODE):
#							sent.append(lemma)
#							if pd.get(lemma):
#								pd[lemma] = pd.get(lemma).add(pos)
#							else:
#								pd[lemma] = { pos }
#				if len(sent) > 0:
#					sentences.append(sent)
				fn = nfname
				if len(sections) > 1:
					fn = re.sub('pkl$', str(section_counter) + '.pkl', fn)
					section_counter = section_counter + 1
				pickleFile = open(os.path.join(pickledir, fn), 'wb')
				pickle.dump(sentences, pickleFile)

#pickleFile = open(pos_dict, 'wb')
#pickle.dump(pd, pickleFile)

sentences = MySentences(pickledir) # a memory-friendly iterator
model = gensim.models.Word2Vec(sentences, workers=4)
model.init_sims(replace=True)
model.save(saved)

shutil.rmtree(pickledir)
