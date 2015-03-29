#!/usr/bin/env python
# -*- coding: utf8 -*-

from os.path import abspath, exists
from os import remove

class FileResource:
    """A resource for a local file"""
    scheme = 'file'

    def __init__(self, url):
        self.url = url
        self.creator_process = None
        self._path = self.get_path()

    def set_creator_process(self, process):
        self.creator_process = process

    def get_path(self):
        return abspath(self.url[len("file://"):])

    def exists(self):
        return exists(self._path)

    def remove(self):
        remove(self._path)
