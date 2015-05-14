# -*- coding: utf8 -*-
from report.html_repport import create_html_report
from pickle import dump, load
from tuttle.invalidation import dependency_map
from tuttle.workflow_runner import create_tuttle_dirs, print_header, print_logs, tuttle_dir, ResourceError, \
    prepare_paths


NO_LONGER_CREATED = "Resource no longer created by the newer process"
NOT_SAME_INPUTS = "Resource was created with different inputs"
PROCESS_CHANGED = "Process code changed"
MUST_CREATE_RESOURCE = "The former primary resource has to be created by tuttle"
RESOURCE_NOT_CREATED_BY_TUTTLE = "The existing resource has not been created by tuttle"
DEPENDENCY_CHANGED = "Resource depends on {} that have changed"


class Workflow:
    """ A workflow is a dependency tree of processes
    """
    def __init__(self, resources):
        self._processes = []
        self._resources = resources
        self._resources_signatures = {}

    def add_process(self, process):
        """ Adds a process
        :param process:
        :return:
        """
        self._processes.append(process)

    def iter_processes(self):
        for process in self._processes:
            yield process

    def iter_resources(self):
        for resource in self._resources.itervalues():
            yield resource

    def missing_inputs(self):
        """ Check that all primary resources (external resources) that are necessary to run the workflow exist
        :return: a list of missing resources
        :rtype: list
        """
        missing = []
        for resource in self._resources.itervalues():
            if resource.is_primary():
                if not resource.exists():
                    missing.append(resource)
        return missing

    def circular_references(self):
        """ Return a list of processes that won't be able to run according to to dependency graph, because
        of circular references, ie when A is produced by B... And B produced by A.
        :return: a list of process that won't be able to run. No special indication about circular groups
        :rtype: list
        """
        resources_to_build = [r for r in self._resources.itervalues() if r.creator_process]
        processes_to_run = [p for p in self.iter_processes()]

        def all_inputs_built(process):
            """ Returns True if all inputs of this process where build, ie if the process can be executed """
            for input_res in process.iter_inputs():
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

        # The idea is to remove the resource from the list as we simulate execution of _processes
        p = pick_a_process()
        while p:
            for r in p.iter_outputs():
                resources_to_build.remove(r)
            processes_to_run.remove(p)
            p = pick_a_process()
        return processes_to_run

    def pick_a_process_to_run(self):
        """ Pick up a process to run
        :return:
        """
        for process in self.iter_processes():
            if process.start is None and process.all_inputs_exists():
                return process
        return None

    def static_check_processes(self):
        """ Runs a pre-check for every process, in order to catch early obvious errors, even before invalidation
        :return: None
        """
        for process in self.iter_processes():
            process.static_check()

    def run_process(self, process):
        reserved_path, log_stdout, log_stderr = prepare_paths(process)
        process.run(reserved_path, log_stdout, log_stderr)
        for res in process.iter_outputs():
            if not res.exists():
                process.post_fail()
                msg = "After execution of process {} : resource {} should have been created".format(process.id,
                                                                                                    res.url)
                raise ResourceError(msg)
        for res in process.iter_outputs():
            self._resources_signatures[res.url] = res.signature()

    def run(self):
        """ Runs a workflow by running every process in the right order

        :return:
        :raises ExecutionError if an error occurs
        """
        create_tuttle_dirs()
        nb_process_run = 0
        process = self.pick_a_process_to_run()
        while process is not None:
            nb_process_run += 1
            print_header(process)
            try:
                self.run_process(process)
            finally:
                self.dump()
                self.create_reports()
                print_logs(process)
            process = self.pick_a_process_to_run()
        return nb_process_run

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
        """
        :param url: Returns the process that creates this url. this url is supposed to be created by this workflow,
        so check creates_url() before calling this method
        :return:
        """
        if url in self._resources:
            return self._resources[url].creator_process

    def find_resource(self, url):
        if url in self._resources:
            return self._resources[url]
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
        assert isinstance(newer_workflow, Workflow), newer_workflow
        changing_resources = []
        for url, resource in self._resources.iteritems():
            newer_resource = newer_workflow.find_resource(url)
            if newer_resource is None:
                if not resource.is_primary():
                    changing_resources.append((resource, NO_LONGER_CREATED))
            elif not newer_resource.is_primary():
                # Only not generated resources need to be invalidated
                if resource.is_primary():
                    changing_resources.append((resource, MUST_CREATE_RESOURCE))
                elif not resource.created_by_same_inputs(newer_resource):
                    changing_resources.append((resource, NOT_SAME_INPUTS))
                elif resource.creator_process._code != newer_resource.creator_process._code:
                    changing_resources.append((resource, PROCESS_CHANGED))
            # Primary resources must not be invalidated
        return changing_resources

    def resources_not_created_by_tuttle(self):
        result = []
        for resource in self._resources.itervalues():
            if not resource.is_primary():
                if resource.url not in self._resources_signatures and resource.exists():
                    result.append(resource)
        return result

    def compute_dependencies(self):
        """ Feeds the dependant_processes field in every resource
        :return: Nothing
        """
        for resource in self._resources.itervalues():
            resource.dependant_processes = []

        for process in self.iter_processes():
            for resource in process.iter_inputs():
                resource.dependant_processes.append(process)

    def retrieve_signatures(self, previous):
        """Retrieve the signatures from the former workflow. Usefull to detect what has changed."""
        for url, signature in previous._resources_signatures.iteritems():
            if url in self._resources:
                self._resources_signatures[url] = signature

    def retrieve_execution_info(self, previous):
        """ Retrieve the execution information of the workflow's processes by getting them from the previous workflow,
         where the processes are in common. Ignore information for the processes that are not in common
         """
        for prev_process in previous.iter_processes():
            prev_output = prev_process.pick_an_output()
            if prev_output and prev_output.url:
                # When running this function, invalidation has been computed already
                # So if process from previous workflow creates a resource, it creates all the same
                # resources as the process in the current workflow
                process = self.find_process_that_creates(prev_output.url)
                if process:
                    process.retrieve_execution_info(prev_process)

    def update_primary_resource_signatures(self):
        """ Updates the list of primary resources with current signatures
         returns the list of resources that have changed
        :return:
        """
        result = []
        for resource in self._resources.itervalues():
            if resource.is_primary():
                signature = resource.signature()
                if resource.url not in self._resources_signatures:
                    self._resources_signatures[resource.url] = signature
                elif self._resources_signatures[resource.url] != signature:
                    self._resources_signatures[resource.url] = signature
                    result.append(resource)
        return result

    def pick_a_failing_process(self):
        for process in self.iter_processes():
            if process.end is not None and process.success is False:
                return process
        return None

    def reset_process_exec_info(self, invalidated_urls):
        for url in invalidated_urls:
            resource = self.find_resource(url)
            if resource and resource.creator_process:
                resource.creator_process.reset_execution_info()