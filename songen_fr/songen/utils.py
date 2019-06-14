#!/usr/bin/env python3
"""
Copyright (c) 2019 Mark Wolff <wolff.mark.b@gmail.com>

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and
this notice are preserved. This file is offered as-is, without any warranty.
"""
import mysql.connector
import sys
from .config import host, mysql_user, mysql_passwd, database

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def connectMySQL():
    cnx = mysql.connector.connect(
      host=host,
      user=mysql_user,
      passwd=mysql_passwd,
      database=database,
      charset='utf8',
      use_unicode=True
    )
    return cnx
