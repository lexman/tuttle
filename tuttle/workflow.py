#!/usr/bin/env python
# -*- coding: utf8 -*-


class Workflow:
    """ A workflow is a dependency tree of processes
    """
    def __init__(self):
        self.processes = []

    def add_process(self, process):
        """ Adds a process
        :param process:
        :return:
        """
        self.processes.append(process)


    def raise_if_missing_inputs(self):
        """Raises a Workflow exception if some inputs are missing"""
        missing_inputs = self.missing_inputs()
        if len(missing_inputs) > 0 :
            missing_txt = ""
            for missing in missing_inputs:
                missing_txt = missing_txt + "* {}\n".format(missing)
            raise WorkflowError("Some resources that are inputs of the workflow "
                                 "are missing : \n{}".format(missing_txt))


    def get_a_process_to_run(self):
        """ Pick up a process to run
        :return:
        """
        pass