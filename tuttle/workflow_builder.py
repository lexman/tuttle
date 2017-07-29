# -*- coding: utf8 -*-

from tuttle.resources import FileResource
from tuttle.processors import *
from tuttle.process import Process
from tuttle.extensions.ext_csv import CSV2SQLiteProcessor
from tuttle.extensions.net import DownloadProcessor, HTTPResource
from tuttle.extensions.postgres import PostgreSQLResource, PostgresqlProcessor
from tuttle.extensions.python import PythonProcessor
from tuttle.extensions.s3 import S3Resource
from tuttle.extensions.sqlite import SQLiteProcessor, SQLiteResource
import os


class WorkflowBuilder():
    """A helper class to build Process classes from the name of processors and resources"""
    
    def __init__(self):
        self._resources_definition = {}
        self._processors = {}
        self.init_resources_and_processors()

    def init_resources_and_processors(self):
        self._resources_definition['file'] = FileResource
        self._resources_definition['http'] = HTTPResource
        self._resources_definition['https'] = HTTPResource
        self._resources_definition['sqlite'] = SQLiteResource
        self._resources_definition['pg'] = PostgreSQLResource
        self._resources_definition['s3'] = S3Resource
        self._processors['shell'] = ShellProcessor()
        self._processors['bat'] = BatProcessor()
        self._processors['python'] = PythonProcessor()
        self._processors['download'] = DownloadProcessor()
        self._processors['sqlite'] = SQLiteProcessor()
        self._processors['postgresql'] = PostgresqlProcessor()
        self._processors['csv2sqlite'] = CSV2SQLiteProcessor()
        if os.name == "nt":
            self._processors['default'] = self._processors['bat']
        else:
            self._processors['default'] = self._processors['shell']

    def extract_scheme(self, url):
        """Extract the scheme from an url
        url is supposed to be stripped from spaces
        """
        separator_pos = url.find('://')
        if separator_pos == -1:
            return False
        url_scheme = url[:separator_pos]
        return url_scheme

    def url_is_empty(self, url):
        """
        :param url:
        :return: True if the url consist only in the scheme without further information
        """
        separator_pos = url.find('://')
        return separator_pos == (len(url) - len('://'))

    def build_resource(self, url):
        scheme = self.extract_scheme(url)
        if scheme is False or scheme not in self._resources_definition:
            return None
        if self.url_is_empty(url):
            return None
        ResDefClass = self._resources_definition[scheme]
        return ResDefClass(url)
    
    def build_process(self, processor, file_name, line_num):
        if processor in self._processors:
            return Process(self._processors[processor], file_name, line_num)
        else:
            return False

    def get_or_build_resource(self, url, resources):
        if url not in resources:
            resource = self.build_resource(url)
            resources[url] = resource
        else:
            resource = resources[url]
        return resource
