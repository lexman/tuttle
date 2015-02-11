#!/usr/bin/env python
# -*- coding: utf8 -*-

from time import time
from jinja2 import Template
from os import path, makedirs

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
            if process.start is None and len(process._outputs) > 0 and not process._outputs[0].exists():
                for in_res in process._inputs:
                    if not in_res.exists():
                        # Can't pick this one if all dependencies have not been generated !
                        continue
                # Every input is here, so the process can be run !
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
            process.start = time()
            process.return_code = process.run(logs_dir)
            process.end = time()
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
