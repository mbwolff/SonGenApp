#!/usr/bin/env python3
"""
Copyright (c) 2020 Mark Wolff <wolff.mark.b@gmail.com>

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and
this notice are preserved. This file is offered as-is, without any warranty.
"""
import epitran
import re
from pathlib import Path

secret_key = b'c-\xf0$\xea\x102\n\xac`\xc5\xbc?VG\x13'
#path = str(Path(__file__).parent.absolute())
# model_file = 'lib/Fievre_model'
# model_file = path + '/' + 'lib/Fievre_model'
model_file = str(Path(__file__).parent.parent.joinpath('lib/Fievre_model').absolute())
#sparse_matrix_file = 'sparse_matrix.npz'
sparse_matrix_file = str(Path(__file__).parent.parent.joinpath('lib/sparse_matrix.npz').absolute())
no_phonemes = 2 # determines the richness of the rhyme
no_verses = 50 # max number of verses presented to user

host = 'localhost'
#host = 'node6160-env-4281256.us.reclaim.cloud'
mysql_user = 'songenappuser'
mysql_passwd = 'use_songenapp'
database = 'songen'

epi = epitran.Epitran('fra-Latn-p')

IPAV = [
    '\u0069', '\u0079', '\u0268', '\u0289', '\u026F', '\u0075',
    '\u026A', '\u028F', '\u026A', '\u0308', '\u028A', '\u0308', '\u028A',
    '\u0065', '\u00F8', '\u0258', '\u0275', '\u0264', '\u006F',
    '\u0259',
    '\u025B', '\u0153', '\u025C', '\u025E', '\u028C', '\u0254',
    '\u00E6', '\u0250',
    '\u0061', '\u0276', '\u0251', '\u0252',
    '\u0329'
#    '\u02D0'
    ]
vowels = re.compile('[' + ''.join(IPAV) + ']')
