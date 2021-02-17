#!/usr/bin/python

activate_this = '/var/www/webroot/songen/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/webroot/ROOT/sgfr")
import os
os.chdir("/var/www/webroot/ROOT/sgfr")
from songen import app as application
