#!/usr/bin/env python
import sys

import gouda

SCRIPTS = ['decode_barcodes']

URL = 'https://github.com/NaturalHistoryMuseum/gouda/'


setup_data = {
    'name': 'gouda',
    'version': gouda.__version__,
    'author': 'Lawrence Hudson',
    'author_email': 'l.hudson@nhm.ac.uk',
    'url': URL,
    'license': 'MIT',
    'description': gouda.__doc__,
    'long_description': 'Visit {0} for more details.'.format(URL),
    'packages': [
        'gouda', 'gouda.engines', 'gouda.java', 'gouda.strategies',
        'gouda.strategies.roi', 'gouda.tests',
    ],
    'include_package_data': True,
    'test_suite': 'gouda.tests',
    'scripts': ['gouda/scripts/{0}.py'.format(script) for script in SCRIPTS],
    'entry_points': {
        'console_scripts':
            ['{0}=gouda.scripts.{0}:main'.format(script) for script in SCRIPTS],
    },
    'install_requires': [
        # TODO How to specify OpenCV? 'cv2>=2.4.8,<3',
        'pathlib>=1.0.1',
        'pylibdmtx>=0.1.1',
        'pyzbar>=0.1.1',
        'numpy>=1.8.2',
    ],
    'tests_require': [
        'nose>=1.3.4',
    ],
    'classifiers': [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ]
}


def setuptools_setup():
    from setuptools import setup
    setup(**setup_data)


if (2, 7) == sys.version_info[:2]:
    setuptools_setup()
else:
    sys.exit('Only Python 2.7 is supported')
