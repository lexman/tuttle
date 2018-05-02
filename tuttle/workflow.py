# -*- coding: utf8 -*-
import sys
from traceback import format_exception

from tuttle.error import TuttleError
from tuttle.report.dot_repport import create_dot_report
from tuttle.report.html_repport import create_html_report
from pickle import dump, load
from tuttle.workflow_runner import WorkflowRunner, TuttleEnv
from tuttle_directories import TuttleDirectories
from tuttle.log_follower import LogsFollower
from tuttle.version import version

class ProcessDependencyIterator:
    """ Provides an iterator on processes according to dependency order"""

    def __init__(self, workflow):
        self._resources_to_build = {r for r in workflow.iter_resources() if r.creator_process}
        self._processes_to_run = {p for p in workflow.iter_processes()}

    def all_inputs_built(self, process):
        """ Returns True if all inputs of this process where build, ie if the process can be executed """
        for input_res in process.iter_inputs():
            if input_res in self._resources_to_build:
                return False
        return True

    def pick_a_process(self):
        """ Pick an executable process, if there is one
        """
        for process in self._processes_to_run:
            if self.all_inputs_built(process):
                return process
        # No more process to pick
        return None

    def iter_processes(self):
        # The idea is to remove the resource from the list as we simulate execution of _processes
        p = self.pick_a_process()
        while p:
            for r in p.iter_outputs():
                self._resources_to_build.remove(r)
            self._processes_to_run.remove(p)
            yield p
            p = self.pick_a_process()

    def remaining(self):
        return self._processes_to_run


class Workflow:
    """ A workflow is a dependency tree of processes
    """
    def __init__(self, resources):
        self._processes = []
        self._preprocesses = []
        self._resources = resources
        self._signatures = {}
        self.tuttle_version = version

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

    def nb_resources(self):
        return len(self._resources)

    def iter_resources(self):
        return self._resources.itervalues()

    def has_preprocesses(self):
        """ Has preprocesses ?
        :return: True if the workflow has preprocesses
        """
        return len(self._preprocesses) > 0

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
        process_iterator = ProcessDependencyIterator(self)
        for _ in process_iterator.iter_processes():
            pass

        return process_iterator.remaining()

    def static_check_processes(self):
        """ Runs a pre-check for every process, in order to catch early obvious errors, even before invalidation
        :return: None
        """
        for process in self.iter_processes():
            process.static_check()

    def check_resources_consistency(self):
        resource_classes = { res.__class__ for res in self.iter_resources()}
        for resource_class in resource_classes:
            resource_class.check_consistency(self)

    def update_signatures(self, signatures):
        """ updates the workflow's signatures after the process has run
        :param signatures: a dictionary of signatures indexed by urls
        """
        self._signatures.update(signatures)

    def run_pre_processes(self):
        """ Runs all the preprocesses

        :return:
        :raises ExecutionError if an error occurs
        """
        TuttleDirectories.create_tuttle_dirs()
        TuttleDirectories.empty_extension_dir()
        if not self.has_preprocesses():
            return
        lt = LogsFollower()
        WorkflowRunner.print_preprocesses_header()
        for process in self.iter_preprocesses():
            TuttleDirectories.prepare_and_assign_paths(process)
            lt.follow_process(process.log_stdout, process.log_stderr, None)

        with lt.trace_in_background(), TuttleEnv():
            for preprocess in self.iter_preprocesses():
                WorkflowRunner.print_preprocess_header(preprocess, lt._logger)
                success = True
                error_msg = None
                try:
                    preprocess.set_start()
                    preprocess.processor.run(preprocess, preprocess._reserved_path,
                                             preprocess.log_stdout, preprocess.log_stderr)
                except TuttleError as e:
                    success = False
                    error_msg = str(e)
                    raise
                except Exception:
                    exc_info = sys.exc_info()
                    stacktrace = "".join(format_exception(*exc_info))
                    error_msg = "An unexpected error have happened in tuttle preprocessor {} : \n" \
                                "{}\n" \
                                "Preprocess {} will not complete.".format(preprocess._processor.name, stacktrace, preprocess.id)
                finally:
                    preprocess.set_end(success, error_msg)
                    self.create_reports()
        WorkflowRunner.print_preprocesses_footer()

    def create_reports(self):
        """ Write to disk files describing the workflow, with color for states
        :return: None
        """
        create_html_report(self, TuttleDirectories.tuttle_dir("report.html"))
        create_dot_report(self, TuttleDirectories.tuttle_dir("report.dot"))

    def dump(self):
        """ Pickles the workflow and writes it to last_workflow.pickle
        :return: None
        """
        with open(TuttleDirectories.tuttle_dir("last_workflow.pickle"), "w") as f:
            dump(self, f)

    def export(self):
        """ Export the workflow for external use : a dump for running tuttle later and a report for human users
        :return: None
        """
        self.dump()
        self.create_reports()


    @staticmethod
    def load():
        try:
            with open(TuttleDirectories.tuttle_dir("last_workflow.pickle"), "r") as f:
                return load(f)
        except:
            return None

    def get_extensions(self):
        return TuttleDirectories.list_extensions()

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
        return self._signatures.iteritems()

    def retrieve_signatures(self, previous):
        """ Retrieve the signatures from the former workflow. Useful to detect what has changed.
            Returns True if some resources where in previous and no longer exist in self
        """
        for url, signature in previous.iter_available_signatures():
            if (url in self._signatures) and (self._signatures[url] == "DISCOVERED"):
                self._signatures[url] = signature

    def pick_a_failing_process(self):
        for process in self.iter_processes():
            if process.end is not None and process.success is False:
                return process
        return None

    def reset_failures(self):
        workflow_changed = False
        for process in self._processes:
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
                    self._signatures[resource.url] = resource.signature()
                else:
                    self._signatures[resource.url] = "DISCOVERED"

    def signature(self, url):
        # TODO simplier with __get__ ?
        if url in self._signatures:
            return self._signatures[url]
        else:
            return None

    def resource_available(self, url):
        return url in self._signatures

    def clear_signatures(self, urls):
        for url in urls:
            if url in self._signatures:
                del self._signatures[url]

    def fill_missing_availability(self):
        for url, signature in self.iter_available_signatures():
            if signature is True:
                print("Filling availability for {}".format(url))
                resource = self.find_resource(url)
                new_signature = resource.signature()
                self._signatures[url] = new_signature

    def similar_process(self, process_from_other_workflow):
        output_resource = process_from_other_workflow.pick_an_output()
        if output_resource:
            return self.find_process_that_creates(output_resource.url)
        else:
            other_wf_urls = process_from_other_workflow.input_urls()
            for process in self.iter_processes():
                if not process.has_outputs() and process.input_urls() == other_wf_urls:
                    return process
        return None

    def iter_processes_on_dependency_order(self):
        """ returns an iterator on processes according to dependency order"""
        process_iterator = ProcessDependencyIterator(self)
        return process_iterator.iter_processes()

    def contains_resource(self, resource):
        return resource.url in self._resources
