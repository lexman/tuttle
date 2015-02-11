#!/usr/bin/env python
# -*- coding: utf8 -*-

from resources import FileResource
from processors import *
from os import path, makedirs


class Process:
    """ Class wrapping a process. A process has some input resources, some output resources, 
    some code that produces outputs from inputs, a processor that handle the language specificities
    """

    def __init__(self, processor, line_num):
        self.start = None
        self.end = None
        self._processor = processor
        self._line_num = line_num
        self._inputs = []
        self._outputs = []
        self._code = None
        self.return_code = None
    
    def add_input(self, input_res):
        self._inputs.append(input_res)

    def add_output(self, output):
        self._outputs.append(output)

    def set_code(self, code):
        self._code = code

    def generate_executable(self):
        directory = path.join(".tuttle", "processes")
        if not path.isdir(directory):
            makedirs(directory)
        self._executable = self._processor.generate_executable(self._code, self._line_num, directory)

    def run(self):
        logs_dir = path.join(path.dirname( self._executable), 'logs')
        if not path.isdir(logs_dir):
            makedirs(logs_dir)
        self._processor.run(self._executable, logs_dir)


class WorkflowBuilder():
    """A helper class to build Process classes from the name of processors and resources"""
    
    def __init__(self):
        self._resources_definition = {}
        self._processors = {}
        self.init_resources_and_processors()

    def init_resources_and_processors(self):
        self._resources_definition['file'] = FileResource
        self._processors['shell'] = ShellProcessor()
        self._processors['bat'] = BatProcessor()
        self._processors['default'] = self._processors['bat']

    def extract_scheme(self, url):
        """Extract the scheme from an url
        url is supposed to be stripped from spaces
        """
        separator_pos = url.find('://')
        if separator_pos == -1:
            return False
        url_scheme = url[:separator_pos]
        return url_scheme

    def build_resource(self, url):
        scheme = self.extract_scheme(url)
        if scheme is False or scheme not in self._resources_definition:
            return None
        ResDefClass = self._resources_definition[scheme]
        return ResDefClass(url)
    
    def build_process(self, line_num, processor=None):
        if processor is None:
            return Process(self._processors["default"], line_num)
        elif processor in self._processors:
            return Process(self._processors[processor], line_num)
        else:
            return False

    def get_or_build_resource(self, url, resources):
        if url not in resources:
            resource = self.build_resource(url)
            resources[url] = resource
        else:
            resource = resources[url]
        return resource
