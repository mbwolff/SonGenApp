"""
Copyright (c) 2019 Mark Wolff <wolff.mark.b@gmail.com>

Copying and distribution of this file, with or without modification, are
permitted in any medium without royalty provided the copyright notice and
this notice are preserved. This file is offered as-is, without any warranty.
"""

from setuptools import find_packages, setup

setup(
    name='songen_en',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'scikit-learn',
        'epitran',
        'gensim',
        'six',
        'mysql.connector',
        'numpy',
        'scipy'
    ],
)
