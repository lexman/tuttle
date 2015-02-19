#!/usr/bin/env python
# -*- coding: utf8 -*-

from os import path, makedirs
from report.dot_repport import create_dot_report
from report.html_repport import create_html_report
from process import ProcessState
from pickle import dump, load


def tuttle_dir(*args):
    return path.join(".tuttle", *args)

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
        directory = tuttle_dir("processes")
        if not path.isdir(directory):
            makedirs(directory)
        for process in self.processes:
            process.generate_executable(directory)

    def run(self):
        """ Runs a workflow that has been previously prepared :

        :return: True if every thing is Ok, False if there war an error while running the processes
        """
        logs_dir = tuttle_dir("processes", 'logs')
        if not path.isdir(logs_dir):
            makedirs(logs_dir)
        process = self.pick_a_process_to_run()
        while process is not None:
            process.run(logs_dir)
            self.dump()
            self.create_reports()
            if process.return_code != 0:
                return False
            process = self.pick_a_process_to_run()
        return True

    def nick_from_url(self, url):
        parts = url.split("/")
        return parts.pop()

    def create_reports(self):
        """ Write to disk files describing the workflow, with color for states
        :return: None
        """
        create_dot_report(self, tuttle_dir("workflow.dot"))
        create_html_report(self, "tuttle_report.html")

    def dump(self):
        """ Pickles the workflow and writes it to last_workflow.pickle

        :return: None
        """
        with open(tuttle_dir("last_workflow.pickle"), "w") as f:
            dump(self, f)

    @staticmethod
    def load():
        try:
            with open(tuttle_dir("last_workflow.pickle"), "r") as f:
                return load(f)
        except:
            return None

    def find_process_that_creates(self, url):
        if url in self.resources:
            return self.resources[url].creator_process
        else:
            return None

    def resources_not_created_the_same_way(self, newer_workflow):
        """
        Returns the list of resources that are not created the same way in the other workflow. Ie :
            - the other workflow doesn't create this resource
            - the other workflow doesn't create this resource from the same inputs
            - the code that produces this resource is different
        :param newer_workflow:
        :return:
        """
        changing_resources = []
        # TODO : could be optimized by not checking twice a process that creates two outputs
        for url, resource in self.resources.iteritems():
            creator_process = resource.creator_process
            if creator_process is not None:
                # Resources not created by a process don't have to be invalidated
                newer_process = newer_workflow.find_process_that_creates(url)
                if newer_process is None:
                    # TODO : if a resource used to be created be by the workflow
                    # but is now a primary input, we should not remove it
                    changing_resources.append(resource)
                elif not resource.creator_process.has_same_inputs(newer_process):
                    changing_resources.append(resource)
                elif resource.creator_process._code != newer_process._code:
                    changing_resources.append(resource)
        # TODO : we could associate a "reason" why the resource is invalid for logs
        return changing_resources

    def compute_dependencies(self):
        """ Feeds the dependant_processes field in every resource
        :return: Nothing
        """
        for resource in self.resources.itervalues():
            resource.dependant_processes = []

        for process in self.processes:
            for resource in process._inputs:
                resource.dependant_processes.append(process)

    def resources_to_invalidate(self, newer_workflow):
        """
        Returns the resources to invalidate in this workflow, before launching newer_workflow
        Other resources are guaranteed to remain the same
        :param newer_workflow:
        :return:
        """
        invalid_resources = self.resources_not_created_the_same_way(newer_workflow)
        self.compute_dependencies()
        for resource in invalid_resources:
            for dependant_process in resource.dependant_processes:
                for dependant_resource in dependant_process._outputs:
                    if dependant_resource not in invalid_resources:
                        invalid_resources.append(dependant_resource)
        return invalid_resources