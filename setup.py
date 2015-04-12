#!/usr/bin/env python
"""Tuttle"""

import sys
from tuttle import __version__
try:
    from setuptools import setup, find_packages
except ImportError:
    print("Tuttle needs setuptools in order to build. Install it using"
          " your package manager (usually python-setuptools) or via pip (pip"
          " install setuptools).")
    sys.exit(1)

setup(name='tuttle',
      version=__version__,
      author='Lexman',
      author_email='tuttle@lexman.org',
      description='Make for data',
      long_description='Reliably create data from source as a team in an industrial environment... A tool for '
                       'continuous data processing',
      platforms=['Linux', 'Windows'],
      url='http://tuttle.lexman.org/',
      license='MIT',
      packages=['tuttle', 'tuttle.report'],
      #data_files=[],
      scripts=[
       'bin/tuttle',
      ],
      include_package_data = True,
      package_data = {
          'tuttle.report' :  ['*.html', 'html_report_assets/*'],
      },
)