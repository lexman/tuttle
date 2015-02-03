#!/usr/bin/env python
# -*- coding: utf8 -*-


class WorkflowError(Exception):
    """An error in the workflow structure"""
    def __init__(self, message):
        super(WorkflowError, self).__init__(message)


class Workflow:
    """ A workflow is a dependency tree of processes
    """
    def __init__(self):
        self.resources = {}
        self.processes = []

    def add_process(self, process):
        """ Adds a process
        :param process:
        :return:
        """
        self.processes.append(process)

    def missing_inputs(self):
        """ Check that all external resources that are necessary to run the workflow exist
        :return: a list of missing resources
        :rtype: list
        """
        missing = []
        for resource in self.resources.itervalues():
            if resource._creator_process is None:
                if not resource.exists():
                    missing.append(resource)
        return missing

    def raise_if_missing_inputs(self):
        """Raises a Workflow exception if some inputs are missing"""
        missings_inputs = self.missing_inputs()
        if len(missings_inputs) > 0 :
            missing_txt = ""
            for missing in missings:
                missing_txt = missing_txt + "* {}\n".format(missing)
            raise WorkflowError("Some resources that are inputs of the workflow "
                                 "are missing : \n{}".format(missing_txt))


    def get_a_process_to_run(self):
        """ Pick up a process to run
        :return:
        """
        pass