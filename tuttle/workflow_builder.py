#!/usr/bin/env python
# -*- coding: utf8 -*-

from resources import FileResource
from processors import *
from time import time
from os import path


class ProcessState:
    SCHEDULED = 0
    READY = 1
    RUNNING = 2
    COMPLETE = 3
    ERROR = 4
    NOTHING_TO_DO = 5


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
        self.log_stdout = None
        self.log_stderr = None
        self.return_code = None
    
    def add_input(self, input_res):
        self._inputs.append(input_res)

    def add_output(self, output):
        self._outputs.append(output)

    def set_code(self, code):
        self._code = code

    def id(self):
        return "{}_{}".format( self._processor.name, self._line_num)

    def generate_executable(self, directory):
        """
        Creates what is needed to later run the process. Commonly, this would be one executable file.
        :param directory: Directory where the executable lies
        :return: An identifier to be able to run the executable later. Commonly, this would be the path to the executable file
        """
        self._executable = self._processor.generate_executable(self._code, self.id(), directory)

    def run(self, logs_dir):
        self.log_stdout = path.join(logs_dir, "{}_stdout".format(self.id()))
        self.log_stderr = path.join(logs_dir, "{}_err".format(self.id()))
        self.start = time()
        self._processor.run(self._executable, self.id(), self.log_stdout, self.log_stderr)
        self.end = time()

    def get_state(self):
        """

        :return: the state of the process.  One of ProcessState value
        """
        if len(self._outputs) == 0:
            return ProcessState.NOTHING_TO_DO
        elif self.start is None:
            for in_res in self._inputs:
                if not in_res.exists():
                    return ProcessState.SCHEDULED
            return ProcessState.READY
        elif self.end is None:
            return ProcessState.RUNNING
        elif self.return_code == 0:
            return ProcessState.COMPLETE
        else:
            return ProcessState.ERROR



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
