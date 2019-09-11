#!/usr/bin/env python3

import os
import logging
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

sgpath = '/var/www/SonGen/sgfr'
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, sgpath)
sys.path.insert(1, '/usr/local/treetagger/bin')
os.chdir(sgpath)
from songen import app as application
eprint('wsgiWD: ' + os.getcwd())
