#!/usr/bin/env python3

import os
import logging
import sys

sgpath = '/var/www/SonGen/sgfr'
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, sgpath)
os.chdir(sgpath)
from songen import app as application
