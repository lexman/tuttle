#!/usr/bin/env python
# -*- coding: utf8 -*-

from jinja2 import Template
from os import path, makedirs
from tuttle.report.dot_repport import create_dot_report
from workflow_builder import ProcessState


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

    def pick_a_process_to_run(self):
        """ Pick up a process to run
        :return:
        """
        #TODO : check for circular references
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
            self.create_dot_report()
            process = self.pick_a_process_to_run()

    def create_html_report(self):
        """ Runs a workflow that has been previously prepared :

        :return: None
        """
        module_dir = path.dirname(__file__)
        tpl_filename = path.join(module_dir, "report", "report_template.html")
        with open(tpl_filename, "r") as ftpl:
            t = Template(ftpl.read())
        with open("report.html", "w") as fout:
            fout.write(t.render(processes = self.processes))

    def nick_from_url(self, url):
        parts = url.split("/")
        return parts.pop()

    def create_dot_report(self):
        """ Write to disk a dot file describing the workflow, with color for states

        :return: None
        """
        create_dot_report(self, "workflow.dot")

    def create_png_report(self):
        """ Runs a workflow that has been previously prepared :

        :return: None
        """
        pass
