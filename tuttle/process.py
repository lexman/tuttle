# -*- coding: utf8 -*-

from time import time


class Process:
    """ Class wrapping a process. A process has some input resources, some output resources, 
    some code that produces outputs from inputs, a processor that handle the language specificities
    """

    def __init__(self, processor, filename, line_num):
        self._start = None
        self._end = None
        self._processor = processor
        self._filename = filename
        self._line_num = line_num
        self._inputs = []
        self._outputs = []
        self._code = ""
        self.log_stdout = None
        self.log_stderr = None
        self._reserved_path = None
        self.success = None
        self._id = "{}_{}".format(self._filename, self._line_num)

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def id(self):
        return self._id

    @property
    def code(self):
        return self._code

    # TODO Use a setter ?
    def set_code(self, code):
        self._code = code

    @property
    def processor(self):
        return self._processor

    def add_input(self, input_res):
        self._inputs.append(input_res)

    def add_output(self, output):
        self._outputs.append(output)

    def iter_inputs(self):
        for res in self._inputs:
            yield res

    def iter_outputs(self):
        for res in self._outputs:
            yield res

    def has_outputs(self):
        return len(self._outputs) > 0

    def has_input(self, resource):
        return resource in self._inputs

    def depends_on_process(self, process):
        """ Returns True if self deprends on a resource created by process"""
        for output_resource in process.iter_outputs():
            if self.has_input(output_resource):
                return True
        return False

    def pick_an_output(self):
        if not self.has_outputs():
            return None
        return self._outputs[0]

    def retrieve_execution_info(self, process):
        """ Copy the execution info (all the properties set by function run()) from another process
        :param process:
        :return:
        """
        self._start = process.start
        self._end = process.end
        self.success = process.success
        self.log_stdout = process.log_stdout
        self.log_stderr = process.log_stderr

    def reset_execution_info(self):
        """ Reset the execution info (all the properties set by function run()) because the resources produced
        by this process have been invalidated
        :return:
        """
        self._start = None
        self._end = None
        self.log_stdout = None
        self.log_stderr = None
        self.success = None

    def static_check(self):
        """
        Runs a verification that the process won't obviously fail. This is used for static analysis before any process
         is run
        """
        self._processor.static_check(self)

    def assign_paths(self, reserved_path, log_stdout, log_stderr):
        assert reserved_path != None
        self._reserved_path = reserved_path
        self.log_stdout = log_stdout
        self.log_stderr = log_stderr

    def set_start(self):
        self._start = time()

    def set_end(self, success):
        self._end = time()
        self.success = success

    def all_inputs_exists(self):
        """
        :return: True if all input resources for this process exist, False otherwise
        """
        for in_res in self.iter_inputs():
            if not in_res.exists():
                return False
        return True

    def missing_outputs(self):
        """
        :return: True if all input resources for this process exist, False otherwise
        """
        result = []
        for resource in self.iter_outputs():
            if not resource.exists():
                result.append(resource)
        return result