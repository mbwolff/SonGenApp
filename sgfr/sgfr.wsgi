#!/usr/bin/env python3

import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/SonGen/sgfr')
from songen import app as application
