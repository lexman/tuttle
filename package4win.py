#!/usr/bin/env python
# -*- coding: utf8 -*-

"""Tuttle"""

import sys
import re
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


def strip_rc(version):
    m = re.search(r'^(\d+)\.(\d+)', version)
    return m.group(0)


# cx_freeze option for a command line application
base = None
build_exe_options = {
    "packages": ["os"],
    "excludes": ["tkinter"],
    "include_files": (
        join("tuttle", "report"),
    )
}
build_msi_options = {
    "add_to_path": True,
}

cx_freeze_opts = {
    'options':  {
        'bdist_msi': build_msi_options,
        'build_exe': build_exe_options
    },
    'executables':  [Executable(join("bin", "tuttle"), base=base)]
}
package_description = tuttle_description
package_description.update(cx_freeze_opts)
package_description['version'] = strip_rc(package_description['version'])
setup(**package_description)