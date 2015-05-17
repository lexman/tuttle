#!/usr/bin/env python
# -*- coding: utf8 -*-

"""Tuttle"""

import sys
from os.path import join
try:
    import setuptools
    from cx_Freeze import setup, Executable
except ImportError:
    print("You need to install setuptools and cx_freeze modules in order to create a Windows installer for tuttle. "
          "You can install these packages with your package manager (usually python-setuptools) or via pip (pip"
          " install setuptools cx_freeze).")
    sys.exit(1)
from setup import tuttle_description # Import description of the package from the standard setup


# cx_freeze option for a command line application
base = None
build_exe_options = {
    "packages": ["os"],
    "excludes": ["tkinter"],
    "include_files": (
        join("tuttle", "report"),
    )
}
cx_freeze_opts = {
    'include_package_data':  True,
    'package_data':  {
        'tuttle.report':  ['*.html', 'html_report_assets/*'],
    },
    'options':  {'build_exe': build_exe_options},
    'executables':  [Executable(join("bin", "tuttle"), base=base)]
}
package_description = tuttle_description.copy()
package_description.update(cx_freeze_opts)

setup(**package_description)