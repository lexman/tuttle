#!/usr/bin/env python
# -*- coding: utf8 -*-

""" Tuttle installation and packaging script """

import sys
import version
try:
    from setuptools import setup, find_packages
except ImportError:
    print("You need to install setuptools to build tuttle. Install it using"
          " your package manager (usually python-setuptools) or via pip (pip"
          " install setuptools).")
    sys.exit(1)



tuttle_description = {
    'name': 'tuttle',
    'version': version.version,
    'author': 'Lexman',
    'author_email': 'tuttle@lexman.org',
    'description': 'Make for data',
    'long_description': 'Reliably create data from different sources. Work as a team in an industrial environment... '
                   'A tool for continuous data processing',
    'platforms': ['Linux', 'Windows'],
    'url': 'http://tuttle.lexman.org/',
    'license': 'MIT',
    'install_requires': ['jinja2', 'MarkupSafe', 'psycopg2'],
    'packages': [
        'tuttle', 
        'tuttle.report', 
        'tuttle.resources',
        'tuttle.processors',
        'tuttle.extensions',
        ],
    'scripts': [
        'bin/tuttle',
    ],
    'include_package_data':  True,
    'package_data':  {
        'tuttle':  ['VERSION'],
        'tuttle.report':  ['*.html', 'html_report_assets/*'],
    },
}


if __name__ == '__main__':
    # NB:  this script can ba imported by windows packager
    version.export_version('tuttle/VERSION')
    setup(**tuttle_description)