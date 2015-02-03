#!/usr/bin/env python
# -*- coding: utf8 -*-


class FileResource:
    """A resource for a local file"""
    scheme = 'file'

    def __init__(self, url):
        self.url = url
        self.creator_process = None

    def set_creator_process(self, process):
        self.creator_process = process

    def exists(self):
        return True
