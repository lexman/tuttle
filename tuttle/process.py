#!/usr/bin/env python
# -*- coding: utf8 -*-

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
        self.inputs = []
        self.outputs = []
        self._code = ""
        self.log_stdout = None
        self.log_stderr = None
        self.return_code = None
    
    def add_input(self, input_res):
        self.inputs.append(input_res)

    def add_output(self, output):
        self.outputs.append(output)

    def set_code(self, code):
        self._code = code

    def retrieve_execution_info(self, process):
        """ Copy the execution info (all the properties set by function run()) from another process
        :param process:
        :return:
        """
        self.start = process.start
        self.end = process.end
        self.return_code = process.return_code
        self.log_stdout = process.log_stdout
        self.log_stderr = process.log_stderr

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
        self.return_code = self._processor.run(self._executable, self.id(), self.log_stdout, self.log_stderr)
        self.end = time()
        return self.return_code

    def has_same_inputs(self, other_process):
        """ Returns True if both process have exactly the same inputs, according to their urls, False otherwise

        :param other_process:
        :return:
        """
        self_inputs = set(in_res.url for in_res in self.inputs)
        other_inputs = set(in_res.url for in_res in other_process.inputs)
        return self_inputs == other_inputs

    def all_inputs_exists(self):
        """
        :return: True if all input resources for this process exist, False otherwise
        """
        for in_res in self.inputs:
            if not in_res.exists():
                return False
        return True
