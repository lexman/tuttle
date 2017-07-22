# -*- coding: utf8 -*-
from report.html_repport import create_html_report
from pickle import dump, load
from tuttlelib.workflow_runner import WorkflowRuner, TuttleEnv
from tuttlelib.log_follower import LogsFollower


NO_LONGER_CREATED = "Resource no longer created by the newer process"
NOT_SAME_INPUTS = "Resource was created with different inputs"
PROCESS_HAS_CHANGED = "Process code has changed"
PROCESSOR_HAS_CHANGED = "Processor has changed"
MUST_CREATE_RESOURCE = "The former primary resource has to be created by tuttle"
RESOURCE_NOT_CREATED_BY_TUTTLE = "The existing resource has not been created by tuttle"
DEPENDENCY_CHANGED = "Resource depends on {} that have changed"
RESOURCE_HAS_CHANGED = "Primary resource has changed"
INCOHERENT_OUTPUTS = "Other outputs produced by the same process are missing"


class Workflow:
    """ A workflow is a dependency tree of processes
    """
    def __init__(self, resources):
        self._processes = []
        self._preprocesses = []
        self._resources = resources
        self._available_resources = {}

    def add_process(self, process):
        """ Adds a process
        :param process:
        :return:
        """
        self._processes.append(process)

    def add_preprocess(self, preprocess):
        """ Adds a preprocess
        :param preprocess:
        :return:
        """
        self._preprocesses.append(preprocess)

    def iter_processes(self):
        for process in self._processes:
            yield process

    def iter_preprocesses(self):
        for preprocess in self._preprocesses:
            yield preprocess

    def iter_resources(self):
        for resource in self._resources.itervalues():
            yield resource

    def has_preprocesses(self):
        """ Has preprocesses ?
        :return: True if the workflow has preprocesses
        """
        return len(self._preprocesses) > 0

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

    def primary_inputs_not_available(self):
        """ Check that all primary resources (external resources) that are necessary to run the workflow are available
        :return: a list of missing resources
        :rtype: list
        """
        missing = []
        for resource in self._resources.itervalues():
            if resource.is_primary():
                if not self.resource_available(resource.url):
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

    def iter_outputless_processes(self):
        for process in self._processes:
            if not process.has_outputs():
                yield process

    def static_check_processes(self):
        """ Runs a pre-check for every process, in order to catch early obvious errors, even before invalidation
        :return: None
        """
        for process in self.iter_processes():
            process.static_check()

    def update_signatures(self, signatures):
        """ updates the workflow's signatures after the process has run
        :param signatures: a dictionary of signatures indexed by urls
        """
        self._available_resources.update(signatures)

    def run_pre_processes(self):
        """ Runs all the preprocesses

        :return:
        :raises ExecutionError if an error occurs
        """
        WorkflowRuner.create_tuttle_dirs()
        WorkflowRuner.empty_extension_dir()
        if not self.has_preprocesses():
            return
        lt = LogsFollower()
        WorkflowRuner.print_preprocesses_header()
        for process in self.iter_preprocesses():
            WorkflowRuner.prepare_and_assign_paths(process)
            lt.follow_process(process.log_stdout, process.log_stderr, process.id)

        with lt.trace_in_background(), TuttleEnv():
            for preprocess in self.iter_preprocesses():
                WorkflowRuner.print_preprocess_header(preprocess, lt._logger)
                try:
                    preprocess.processor.run(preprocess, preprocess._reserved_path,
                                             preprocess.log_stdout, preprocess.log_stderr)

                finally:
                    self.create_reports()
            WorkflowRuner.print_preprocesses_footer()

    def create_reports(self):
        """ Write to disk files describing the workflow, with color for states
        :return: None
        """
        create_html_report(self, WorkflowRuner.tuttle_dir("report.html"))

    def dump(self):
        """ Pickles the workflow and writes it to last_workflow.pickle
        :return: None
        """
        with open(WorkflowRuner.tuttle_dir("last_workflow.pickle"), "w") as f:
            dump(self, f)

    @staticmethod
    def load():
        try:
            with open(WorkflowRuner.tuttle_dir("last_workflow.pickle"), "r") as f:
                return load(f)
        except:
            return None

    def get_extensions(self):
        return WorkflowRuner.list_extensions()

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
                elif resource.creator_process.code != newer_resource.creator_process.code:
                    changing_resources.append((resource, PROCESS_HAS_CHANGED))
                elif resource.creator_process.processor.name != newer_resource.creator_process.processor.name:
                    changing_resources.append((resource, PROCESSOR_HAS_CHANGED))
            # Primary resources must not be invalidated
        return changing_resources

    def failed_resources(self):
        """
        Returns the list of resources that would have been produced by processes that have failed
        :return:
        """
        result = []
        for process in self._processes:
            if process.success is False:
                result.extend(process.iter_outputs())
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

    def iter_available_signatures(self):
        for url, signature in self._available_resources.iteritems():
            yield url, signature

    def retrieve_signatures(self, previous):
        """ Retrieve the signatures from the former workflow. Useful to detect what has changed.
            Returns True if some resources where in previous and no longer exist in self
        """
        for url, signature in previous.iter_available_signatures():
            if url in self._resources:
                if url in self._available_resources and self._available_resources[url] == "AVAILABLE":
                    self._available_resources[url] = signature

    def removed_resources(self, previous):
        """ Retrieve the signatures from the former workflow. Useful to detect what has changed.
            Returns True if some resources where in previous and no longer exist in self
        """
        for url, signature in previous.iter_available_signatures():
            if url not in self._resources:
                return True
        return False

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

    def reset_modified_outputless_processes(self, prev_workflow):
        workflow_changed = False
        for prev_process in prev_workflow.iter_processes():
            if not prev_process.has_outputs():
                process = self.find_outputless_process_with_same_inputs(prev_process)
                if process and (prev_process.code != process.code or
                                prev_process.processor.name != process.processor.name):
                    process.reset_execution_info()
                    workflow_changed = True
        return workflow_changed

    def reset_failing_outputless_process_exec_info(self):
        workflow_changed = False
        for process in self._processes:
            if not process.has_outputs():
                if process.success is False:
                    process.reset_execution_info()
                    workflow_changed = True
        return workflow_changed

    def all_inputs_available(self, process):
        """
        :return: True if all input resources for this process are vailable, False otherwise
        """
        for in_res in process.iter_inputs():
            if not self.resource_available(in_res.url):
                return False
        return True

    def runnable_processes(self):
        """ List processes that can be run (because they have all inputs)
        :return:
        """
        res = set()
        for process in self.iter_processes():
            if process.start is None and self.all_inputs_available(process):
                res.add(process)
        return res

    def discover_runnable_processes(self, complete_process):
        """ List processes that can be run (because they have all inputs)
        :return:
        """
        res = set()

        for process in self.iter_processes():
            if process.start is None:
                if process.depends_on_process(complete_process):
                    if self.all_inputs_available(process):
                        res.add(process)
        return res

    def discover_resources(self):
        for resource in self._resources.itervalues():
            if resource.exists():
                if resource.is_primary():
                    self._available_resources[resource.url] = resource.signature()
                else:
                    self._available_resources[resource.url] = "AVAILABLE"

    def signature(self, url):
        # TODO simplier with __get__ ?
        if url in self._available_resources:
            return self._available_resources[url]
        else:
            return None

    def resource_available(self, url):
        return url in self._available_resources

    def modified_primary_resources(self, older_workflow):
        """ List the resources that have changed
         returns the list of resources that have changed
        :return:
        # TODO : could check for modified resources, not only primaries for advanced check
        """
        result = []
        for resource in self._resources.itervalues():
            if resource.is_primary():
                if older_workflow.signature(resource.url) != self._available_resources[resource.url]:
                    result.append(resource)
        return result

    def incoherent_outputs_from_successfull_processes(self):
        """ returns the list of resources of each process where some outputs are missing
        :return:
        """
        result = []
        for process in self._processes:
            if process.success:
                missing = False
                for resource in process.iter_outputs():
                    if not self.resource_available(resource.url):
                        missing = True
                        break
                if missing:
                    for resource in process.iter_outputs():
                        if self.resource_available(resource.url):
                            result.append((resource, INCOHERENT_OUTPUTS))
        return result

    def resources_not_created_by_tuttle(self, previous_workflow):
        result = []
        for resource in self._resources.itervalues():
            if not resource.is_primary():
                if self.resource_available(resource.url):
                    if not previous_workflow or not previous_workflow.resource_available(resource.url):
                        result.append(resource)
        return result

    def find_outputless_process_with_same_inputs(self, process_from_other_workflow):
        other_wf_urls = process_from_other_workflow.input_urls()
        for process in self.iter_processes():
            if not process.has_outputs() and process.input_urls() == other_wf_urls:
                return process
        return None

    def similar_process(self, process_from_other_workflow):
        output_resource = process_from_other_workflow.pick_an_output()
        if output_resource:
            return self.find_process_that_creates(output_resource.url)
        else:
            other_wf_urls = process_from_other_workflow.input_urls()
            for process in self.iter_processes():
                if process.input_urls() == other_wf_urls:
                    return process
        return None

    def retrieve_execution_info(self, previous):
        """ Retrieve the execution information of the workflow's processes by getting them from the previous workflow,
         where the processes are in common. Ignore information for the processes that are not in common
         """
        for prev_process in previous.iter_processes():
            prev_output = prev_process.pick_an_output()
            if prev_output:
                process = self.find_process_that_creates(prev_output.url)
            else:
                # process with neither inputs nor outputs are not allowed
                # neither two outputless processes without same inputs
                # Also if the process isn't similar enough, it will be invalidated later
                process = self.find_outputless_process_with_same_inputs(prev_process)
            if process:
                process.retrieve_execution_info(prev_process)

    def clear_signatures(self, urls):
        for url in urls:
            if url in self._available_resources:
                del self._available_resources[url]