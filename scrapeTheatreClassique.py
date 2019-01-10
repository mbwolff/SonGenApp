#!/usr/bin/env python3
"""
Copyright (c) 2019 Mark Wolff <wolff.mark.b@gmail.com>

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and
this notice are preserved. This file is offered as-is, without any warranty.
"""

import os
import requests
from bs4 import BeautifulSoup

sourcepage = 'http://www.theatre-classique.fr/pages/programmes/PageEdition.php'
sourcedir = 'http://www.theatre-classique.fr/pages/documents/'
# These links worked on 29 November 2018
destdir = '../Fievre'

if not os.path.exists(destdir):
    os.makedirs(destdir)

r = requests.get(sourcepage)
soup = BeautifulSoup(r.text, 'html.parser')
for link in soup.find_all('a'):
    if link.get('href').endswith('xml'):
        file = link.get('href').split('/').pop(-1)
        print(file)
        doc = requests.get(sourcedir + file)
        local_file = open(os.path.join(destdir, file), 'w')
        local_file.write(doc.text.encode('utf8'))
        local_file.close()
