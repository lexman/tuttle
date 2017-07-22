# -*- coding: utf8 -*-
from os.path import dirname, join, getsize
import sys


def module_path():
    if getattr(sys, 'frozen', False):
        # The application is frozen
        return join(dirname(sys.executable), "tuttlelib")
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        return dirname(__file__)


def get_version():
    version_path = join(module_path(), "VERSION")
    version_details = open(version_path).read(getsize(version_path))
    return version_details.split("\n")[0]


version = get_version()

