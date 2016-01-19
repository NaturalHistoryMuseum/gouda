#!/usr/bin/env python
from setuptools import setup

import gouda

setup(name='gouda',
      version=gouda.__version__,
      description=gouda.__doc__,
      author='Lawrence Hudson',
      author_email='l.hudson@nhm.ac.uk',
      packages=['gouda', 'gouda.engines', 'gouda.java', 'gouda.strategies',
                'gouda.strategies.roi'],
      test_suite = "gouda.tests",
      scripts=['gouda/bin/decode_barcode.py'],
      install_requires=[l.replace('==', '>=') for l in open('requirements.txt')],
     )
