#!/usr/bin/env python
# -*- coding: utf8 -*-

"""Tuttle"""

import sys
from os.path import join
from tuttle import __version__
try:
    from setuptools import setup, find_packages
    from cx_Freeze import setup, Executable
except ImportError:
    print("Tuttle needs setuptools and cx_freeze modules in order to build and package. Install it using"
          " your package manager (usually python-setuptools) or via pip (pip"
          " install setuptools cx_freeze).")
    sys.exit(1)

# cx_freeze option for a command line application
base = None

build_exe_options = {
    "packages": ["os"],
    "excludes": ["tkinter"],
    "include_files": (
        join("tuttle", "report"),
    )
}

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
      install_requires=['jinja2'],
      packages=['tuttle', 'tuttle.report'],
      scripts=[
       'bin/tuttle',
      ],
      include_package_data = True,
      package_data = {
          'tuttle.report' :  ['*.html', 'html_report_assets/*'],
      },
      options = {"build_exe": build_exe_options},
      executables = [Executable(join("bin", "tuttle"), base=base)],
)