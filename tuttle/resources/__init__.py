#!/usr/bin/env python
# -*- coding: utf8 -*-

from os.path import abspath, exists

class FileResource:
    """A resource for a local file"""
    scheme = 'file'

    def __init__(self, url):
        self.url = url
        self.creator_process = None

    def set_creator_process(self, process):
        self.creator_process = process

    def get_path(self):
        return abspath(self.url[len("file://"):])

    def exists(self):
        file_path = self.get_path()
        print file_path
        return exists(file_path)
