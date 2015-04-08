# -*- coding: utf8 -*-
from shutil import rmtree
from os.path import isdir, isfile

from error import TuttleError
from os import path, makedirs, remove
from report.html_repport import create_html_report
from pickle import dump, load


class ExecutionError(TuttleError):
    def __init__(self, message):
        self._message = message

    def __str__(self):
        return "Error while running the workflow : \n{}".format(self._message)


class ProcessExecutionError(ExecutionError):
    pass


class ResourceError(ExecutionError):
    pass


class InvalidationReason:
    NO_LONGER_CREATED = 0
    NOT_SAME_INPUTS = 1
    PROCESS_CHANGED = 2
    RESOURCE_NOT_CREATED_BY_TUTTLE = 3
    DEPENDENCY_CHANGED = 4

    messages = [
        "Resource no longer created by the newer process",
        "Resource was created with different inputs",
        "Process code changed",
        "Resource has not been created by tuttle",
        "Resource depends on another resource that have changed",
    ]

    def __init__(self, reason):
        self._reason = reason

    def __str__(self):
        return self.messages[self._reason]


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

    def circular_references(self):
        """ Return a list of processes that won't be able to run according to to dependency graph, because
        of circular references, ie when A is produced by B... And B produced by A.
        :return: a list of process that won't be able to run. No special indication about circular groups
        :rtype: list
        """
        resources_to_build = [r for r in self.resources.itervalues() if r.creator_process]
        processes_to_run = [p for p in self.processes]

        def all_inputs_built(process):
            """ Returns True if all inputs of this process where build, ie if the process can be executed """
            for input_res in process.inputs:
                if input_res in resources_to_build:
                    return False
            return True

        def pick_a_process():
            """ Pick an executable process, if there is one
            """
            for process in processes_to_run:
                if all_inputs_built(process):
                    return process
            # No more process to pick
            return None

        # The idea is to remove the resource from the list as we simulate execution of processes
        p = pick_a_process()
        while p:
            for r in p.outputs:
                resources_to_build.remove(r)
            processes_to_run.remove(p)
            p = pick_a_process()
        return processes_to_run

    def pick_a_process_to_run(self):
        """ Pick up a process to run
        :return:
        """
        for process in self.processes:
            if process.start is None and process.all_inputs_exists():
                return process
        return None

    def pre_check_processes(self):
        """ Runs a pre-check for every process, in order to catch early obvious errors, even before invalidation
        :return: None
        """
        for process in self.processes:
            process.pre_check()

    def run_process(self, process):
        reserved_path, log_stdout, log_stderr = self.prepare_paths(process)
        process.run(reserved_path, log_stdout, log_stderr)
        self.dump()
        self.create_reports()
        if process.success is False:
            msg = "Process {} ended with error code {}".format(process.id, process.return_code)
            raise ProcessExecutionError(msg)
        for res in process.outputs:
            if not res.exists():
                msg = "After execution of process {} : resource {} should have been created".format(process.id,
                                                                                                    res.url)
                raise ResourceError(msg)

    def create_tuttle_dirs(self):
        self._processes_dir = tuttle_dir("processes")
        if not path.isdir(self._processes_dir):
            makedirs(self._processes_dir)
        self._logs_dir = tuttle_dir("processes", 'logs')
        if not path.isdir(self._logs_dir):
            makedirs(self._logs_dir)

    def prepare_paths(self, process):
        log_stdout = path.join(self._logs_dir, "{}_stdout".format(process.id))
        log_stderr = path.join(self._logs_dir, "{}_err".format(process.id))
        reserved_path = path.join(self._processes_dir, process.id)
        if isdir(reserved_path):
            rmtree(reserved_path)
        elif isfile(reserved_path):
            remove(reserved_path)
        return reserved_path, log_stdout, log_stderr

    def run(self):
        """ Runs a workflow by running every process in the right order

        :return:
        :raises ExecutionError if an error occurs
        """
        self.create_tuttle_dirs()
        process = self.pick_a_process_to_run()
        while process is not None:
            self.run_process(process)
            process = self.pick_a_process_to_run()

    def nick_from_url(self, url):
        parts = url.split("/")
        return parts.pop()

    def create_reports(self):
        """ Write to disk files describing the workflow, with color for states
        :return: None
        """
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
                    changing_resources.append((resource, InvalidationReason(InvalidationReason.NO_LONGER_CREATED)))
                elif not resource.creator_process.has_same_inputs(newer_process):
                    changing_resources.append((resource, InvalidationReason(InvalidationReason.NOT_SAME_INPUTS)))
                elif resource.creator_process._code != newer_process._code:
                    changing_resources.append((resource, InvalidationReason(InvalidationReason.PROCESS_CHANGED)))
        return changing_resources

    def resources_not_created_by_tuttle(self):
        result = []
        for resource in self.resources.itervalues():
            if resource.exists() and resource.creator_process and resource.creator_process.end is None:
                result.append((resource, InvalidationReason(InvalidationReason.RESOURCE_NOT_CREATED_BY_TUTTLE)))
        return result

    def compute_dependencies(self):
        """ Feeds the dependant_processes field in every resource
        :return: Nothing
        """
        for resource in self.resources.itervalues():
            resource.dependant_processes = []

        for process in self.processes:
            for resource in process.inputs:
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
        for (resource, _) in invalid_resources:
            for dependant_process in resource.dependant_processes:
                for dependant_resource in dependant_process.outputs:
                    if dependant_resource not in invalid_resources:
                        invalid_resources.append( (dependant_resource, InvalidationReason(InvalidationReason.DEPENDENCY_CHANGED)) )
        return invalid_resources

    def retrieve_execution_info(self, previous, invalidated_resources):
        """ Retrieve the execution information of the workflow's processes by getting them from the previous workflow, where the processes are in common
         No need to retrieve information for the processes that are not in common
         """
        inv_urls = [res[0].url for res in invalidated_resources]
        for prev_process in previous.processes:
            if len(prev_process.outputs) > 0 and prev_process.outputs[0].url not in inv_urls:
                # When running this function, invalidation has been computed already
                # So if process from previous workflow creates a resource, it creates all the same
                # resources as the process in the current workflow
                process = self.find_process_that_creates(prev_process.outputs[0].url)
                process.retrieve_execution_info(prev_process)
                pass

    def pick_a_failing_process(self):
        for process in self.processes:
            if process.end is not None and process.success is False:
                return process
        return None
