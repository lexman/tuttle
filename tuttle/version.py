# -*- coding: utf8 -*-
from os.path import dirname, join, getsize
import sys


def module_path():
    if getattr(sys, 'frozen', False):
        # The application is frozen
        return dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        return dirname(__file__)


def read_version_file():
    version_path = join(module_path(), "VERSION")
    version_details = open(version_path).read(getsize(version_path))
    return tuple(version_details.split("\n")[:3])


version, commit_id, plateform = read_version_file()

