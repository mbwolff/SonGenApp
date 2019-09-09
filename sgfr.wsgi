#! /usr/bin/python3

import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/www/var/html/SonGen/sgfr')
from songen import app as application
