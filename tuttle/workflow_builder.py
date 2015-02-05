#!/usr/bin/env python
# -*- coding: utf8 -*-

from resources import FileResource
from processors import ShellProcessor


class Process:
    """ Class wrapping a process. A process has some input resources, some output resources, 
    some code that produces outputs from inputs, a processor that handle the language specificities
    """    
    def __init__(self, processor):
        self._processor = processor
        self._inputs = []
        self._outputs = []
        self._code = None
    
    def add_input(self, input_res):
        self._inputs.append(input_res)

    def add_output(self, output):
        self._outputs.append(output)

    def set_code(self, code):
        self._code = code


class WorkflowBuilder():
    """A helper class to build Process classes from the name of processors and resources"""
    
    def __init__(self):
        self._resources_definition = {}
        self._processors = {}
        self.init_resources_and_processors()

    def init_resources_and_processors(self):
        self._resources_definition['file'] = FileResource
        self._processors['shell'] = ShellProcessor
        self._processors['default'] = ShellProcessor

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
            print self._resources_definition
            return None
        ResDefClass = self._resources_definition[scheme]
        return ResDefClass(url)
    
    def build_process(self, processor=None):
        if processor is None:
            return Process(self._processors["default"])
        elif processor in self._processors:
            return Process(self._processors[processor])
        else:
            return False

    def get_or_build_resource(self, url, resources):
        if url not in resources:
            resource = self.build_resource(url)
            resources[url] = resource
        else:
            resource = resources[url]
        return resource
