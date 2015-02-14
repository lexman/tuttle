#!/usr/bin/env python
# -*- coding: utf8 -*-

from os import path, makedirs
from report.dot_repport import create_dot_report
from report.html_repport import create_html_report
from workflow_builder import ProcessState


class Workflow:
    """ A workflow is a dependency tree of processes
    """
    def __init__(self):
        self.processes = []
        self.resources = None

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
            if resource.creator_process is None:
                if not resource.exists():
                    missing.append(resource)
        return missing

    def pick_a_process_to_run(self):
        """ Pick up a process to run
        :return:
        """
        # TODO : check for circular references
        for process in self.processes:
            # All outputs are supposed to be generated at the same time with a process,
            # so checking for existence of one is like checking fo existence of all !
            if process.get_state() == ProcessState.READY:
                return process
        return None

    def prepare(self):
        """ Prepare the workflow to be executed :
        - creates executable
        - ...
        The workflow is supposed to be safe : no circular references, etc.

        :return: None
        """
        directory = path.join(".tuttle", "processes")
        if not path.isdir(directory):
            makedirs(directory)
        for process in self.processes:
            process.generate_executable(directory)

    def run(self):
        """ Runs a workflow that has been previously prepared :

        :return: None
        """
        logs_dir = path.join(".tuttle", "processes", 'logs')
        if not path.isdir(logs_dir):
            makedirs(logs_dir)
        process = self.pick_a_process_to_run()
        while process is not None:
            process.run(logs_dir)
            self.create_reports()
            process = self.pick_a_process_to_run()

    def nick_from_url(self, url):
        parts = url.split("/")
        return parts.pop()

    def create_reports(self):
        """ Write to disk files describing the workflow, with color for states
        :return: None
        """
        create_dot_report(self, "workflow.dot")
        create_html_report(self, "report.html")
