# SonGen
## A sonnet generator

This code will be presented at the [2019 Electronic Literature Organization's conference in Cork, Ireland](http://elo2019.ucc.ie).

There are two Python modules in this repository, one for generating sonnets in French and the other in English. There really should be one master module that can be parameterized for specific languages and corpora, but I leave that project for another day. Both modules are very similar and differ only in the way they handle source data and scansion rules (alexandrines or pentameters, for instance).

## Setup

You will need to install the following Python modules (the current repo works for Python 3.7):

* [this fork](https://github.com/mbwolff/epitran) of epitran (I have written custom rules for transliterating French verse into IPA: you do not need this fork if you will only use the English sonnet generator).
* mysql.connector
* [treetagger-python](https://github.com/miotto/treetagger-python) (already included here, but I wanted to acknowledge the author)
* gensim
* flask
