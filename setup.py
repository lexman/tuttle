#!/usr/bin/env python
# -*- coding: utf8 -*-

""" Tuttle installation and packaging script """

import sys
from os.path import dirname, getsize, join

try:
    from setuptools import setup, find_packages
except ImportError:
    print("You need to install setuptools to build tuttle. Install it using"
          " your package manager (usually python-setuptools) or via pip (pip"
          " install setuptools).")
    sys.exit(1)


def get_version():
    version_path = join(dirname(__file__), 'tuttlelib', 'VERSION')
    version_details = open(version_path).read(getsize(version_path))
    return version_details.split("\n")[0]


version = get_version()

tuttle_description = {
    'name': 'tuttle',
    'version': version,
    'author': 'Lexman',
    'author_email': 'tuttle@lexman.org',
    'description': 'Make for data',
    'long_description': 'Reliably create data from different sources. Work as a team in an industrial environment... '
                        'A tool for continuous data processing',
    'platforms': ['Linux', 'Windows'],
    'url': 'http://tuttle.lexman.org/',
    'license': 'MIT',
    'install_requires': ['jinja2', 'MarkupSafe', 'psycopg2', 'six', 'boto3', 'chardet', 'psutil'],
    'packages': [
        'tuttlelib',
        'tuttlelib.report',
        'tuttlelib.resources',
        'tuttlelib.processors',
        'tuttlelib.extensions',
    ],
    'entry_points': {
        'console_scripts': [
            'tuttle=tuttlelib.entry_points:tuttle_main',
            'tuttle-extend-workflow=tuttlelib.entry_points:tuttle_extend_workflow_main',
        ],
    },
    'include_package_data': True,
    'package_data': {
        'tuttlelib': ['VERSION'],
        'tuttlelib.report': ['*.html', 'html_report_assets/*'],
    },
}


if __name__ == '__main__':
    # NB:  this script can ba imported by windows packager
    setup(**tuttle_description)