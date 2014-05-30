
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'A Python project aiming at finding homogeneous sub columns of a free text column',
    'author': 'Patrick Westphal',
    'url': 'https://github.com/patrickwestphal/colsplit',
    'download_url': 'https://github.com/patrickwestphal/colsplit',
    'author_email': 'patrick.westphal@informatik.uni-leipzig.de',
    'version': '0.0.1',
    'install_requires': [
      'numpy',
      'nose'
    ],
    'packages': ['colsplit'],
    'scripts': ['bin/colsplit'],
    'name': 'colsplit'
}

setup(**config)
