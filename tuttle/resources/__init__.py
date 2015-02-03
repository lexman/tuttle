#!/usr/bin/env python
# -*- coding: utf8 -*-


class FileResource:
    """A resource for a local file"""
    scheme = 'file'

    def __init__(self, url):
        self._url = url
        self._creator_process = None

    def set_creator_process(self, process):
        self._creator_process = process

    def exists(self):
        return True
