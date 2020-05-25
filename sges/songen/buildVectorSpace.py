#!/usr/bin/env python3
"""
Copyright (c) 2020 Mark Wolff <wolff.mark.b@gmail.com>

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and
this notice are preserved. This file is offered as-is, without any warranty.
"""

import os
import pickle
import re
import csv
import logging
import gensim
import shutil
import xml.etree.ElementTree as ET
from six import iteritems
from utils import eprint, tag
from config import tagdir

sourcedir = '/media/psf/Home/Research/2019 SonGen/CorpusSonetosSigloDeOro'

pickledir = 'Sonetos_pickled'
saved = os.path.join('../lib', re.sub('pickled$', 'model', pickledir))

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
if not os.path.exists(pickledir):
    os.makedirs(pickledir)

num_files = 0
for dname in os.listdir(sourcedir):
	if dname in ['GuiaAnotacionMetrica.pdf', 'README_esp.md', 'README.md']:
		continue
	for fname in os.listdir(os.path.join(sourcedir, dname)):
		if fname.endswith('xml'):
			num_files = num_files + 1
			nfname = re.sub('xml$', 'pkl', fname)
			if os.path.exists(os.path.join(pickledir, nfname)):
				print('Already have ' + nfname)
				continue
			with open(os.path.join(sourcedir, dname, fname), 'rb') as myfile:
				string = myfile.read()
			root = ET.fromstring(string)

			eprint(str(num_files) + ' ' + fname)
#			string = str()
			work = list()
#			ln = ''
			for line in root.findall('.//{http://www.tei-c.org/ns/1.0}l'):
				verse = line.text
#				id = line.attrib['n']
#				if id == ln or ln == '':
#					string = string + ' ' + verse
#				else:
#					work.append(re.sub('^\s+', '', string))
#					string = verse
#				ln = id
#				work.append(re.sub('^\s+', '', string))
				work.append(re.sub('^\s+', '', verse))

#			sections = []
#			current_section = ''
#			last_chunk = work.pop()
#			for chunk in work:
#				if len(current_section) + len(chunk) + 1 < 1000000:
#				# Spacy requires texts of length no more than 1000000
#					current_section = current_section + ' ' + chunk
#				else:
#					sections.append(current_section)
#					current_section = chunk
#
#			current_section = current_section + last_chunk
#			sections.append(re.sub('^\s+', '', current_section))

#			section_counter = 0
#			for section in sections:
			text = ' '.join(work)
			sentences = list()
			sent = list()
#			for t in tag(section):
			for t in tag(text):
#					eprint(t)
				if len(t) < 2:
					continue
				elif t[2].lower() == '<unknown>':
					t[2] = t[0]
				sent.append(t[2].lower())
				if t[1] == 'FS':
					sentences.append(sent)
					sent = list()
			if len(sent) >= 2:
				sentences.append(sent)

#			fn = nfname
#			if len(sections) > 1:
#				fn = re.sub('pkl$', str(section_counter) + '.pkl', fn)
#				section_counter = section_counter + 1
			pickleFile = open(os.path.join(pickledir, nfname), 'wb')
			pickle.dump(sentences, pickleFile)
			pickleFile.close()

sentences = MySentences(pickledir) # a memory-friendly iterator
model = gensim.models.Word2Vec(sentences, workers=4)
model.init_sims(replace=True)
model.save(saved)

shutil.rmtree(pickledir)
