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

    def get_a_process_to_run(self):
        """ Pick up a process to run
        :return:
        """
        pass