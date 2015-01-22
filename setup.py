#!/usr/bin/env python
"""Tuttle"""
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

config = {
	'name' : 'tuttle',
    'version' : '0.1',
    'description' : 'Make for data',
    'long_description' : 'Reliably create data from source as a team in an industrial environment... A tool for continuous data processing',
    'author' : 'Lexman',
    'author_email' : 'tuttle@lexman.org',
    'platforms' : ['Linux', 'Windows'],
    'url' : 'http://tuttle.lexman.org/',
    'install_requires': ['nose'],
    'license' : 'MIT',
    'packages' : find_packages(),
    'scripts': [],
}

setup(**config)	