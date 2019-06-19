# SonGenApp
## A sonnet generator

This code will be presented at the [2019 Electronic Literature Organization's conference in Cork, Ireland](http://elo2019.ucc.ie).

There are two Python modules in this repository, one for generating sonnets in French and the other in English. There really should be one master module that can be parameterized for specific languages and corpora, but I leave that project for another day. Both modules are very similar and differ only in the way they handle source data and scansion rules (alexandrines or pentameters, for instance).

## Setup

You will need to install the following Python modules (the current repo works for Python 3.7):

* [this fork of epitran](https://github.com/mbwolff/epitran) (I have written custom rules for transliterating French verse into IPA: you do not need this fork if you will only use the English sonnet generator).
* [mysql.connector](https://dev.mysql.com/doc/connector-python/en/)
* [treetagger-python](https://github.com/miotto/treetagger-python) (already included here, but I want to acknowledge the source)
* [gensim](https://radimrehurek.com/gensim/)
* [flask](http://flask.pocoo.org)
