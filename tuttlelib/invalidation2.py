# -*- coding: utf8 -*-
from itertools import chain

NOT_PRODUCED_BY_TUTTLE = "The existing resource has not been produced by tuttle"
USER_REQUEST = "User request"
PROCESS_HAS_FAILED = "The resource has been produced by a failing process"
NO_LONGER_CREATED = "Resource no longer created by the newer process"
NOT_SAME_INPUTS = "Resource was created with different inputs"
PROCESS_HAS_CHANGED = "Process code has changed"
PROCESSOR_HAS_CHANGED = "Processor has changed"
MUST_CREATE_RESOURCE = "The former primary resource has to be created by tuttle"  # Is it a subscase of NOT_PRODUCED_BY_TUTTLE ?
RESOURCE_NOT_CREATED_BY_TUTTLE = "The existing resource has not been created by tuttle"
RESOURCE_HAS_CHANGED = "Primary resource has changed"
INCOHERENT_OUTPUTS = "Other outputs produced by the same process are missing"
DEPENDENCY_CHANGED = "Resource depends on {} that have changed"
BROTHER_INVALID = "Resource is created along with {} that is invalid"
BROTHER_MISSING = "Resource is created along with {} that is missing"


class InvalidCollector:
    """ This class class collects the resources to invalidate and their reason, in order to display them to the user
    and remove them all at once.
    Resources can come from several workflows (eg the current and the previous one)
    """
    def __init__(self, previous_workflow):
        self._resources_and_reasons = []
        self._resources_urls = set()
        self._processes = []
        self._previous_processes = []
        self._previous_workflow = previous_workflow

    def iter_urls(self):
        for url in self._resources_urls:
            yield url

    def resource_invalid(self, url):
        return url in self._resources_urls

    def resources_to_invalidate(self):
        return self._resources_urls

    def something_to_invalidate(self):
        return self._resources_urls or self._previous_processes or self._processes

    def duration(self):
        all_processes = (process for process in chain(self._previous_processes, self._processes))
        duration_sum = sum( (process.end - process.start for process in all_processes if process.end is not None) )
        return int(duration_sum)

    def warn_and_abort_on_threshold(self, threshold):
        aborted = False
        if self._resources_and_reasons:  # BETTER TEST NEEDED HERE
            inv_duration = self.duration()
            print "The following resources are not valid any more and will be removed :"
            for resource, reason in self._resources_and_reasons:
                print("* {} - {}".format(resource.url, reason))
            if -1 < threshold <= inv_duration:
                msg = "You were about to loose {} seconds of processing time (which exceeds the {} seconds " \
                      "threshold). \nAborting... ".format(inv_duration, threshold)
                print msg
                aborted = True
            else:
                print("{} seconds of processing will be lost".format(inv_duration))
        return aborted

    def remove_resources(self, workflow):
        for resource, reason in self._resources_and_reasons:
            # if resource is from the workflow, we know its availability
            # but we have to check existence if it comes from the previous workflow
            if (workflow.contains_resource(resource) and workflow.resource_available(resource.url)) \
                    or resource.exists():
                try:
                    resource.remove()
                except Exception as e:
                    msg = 'Warning : Removing resource {} has failed. Even if the resource is still available, ' \
                          'it should not be considered valid.'.format(resource.url)
                    print(msg)

    def reset_execution_info(self):
        for process in self._processes:
            process.reset_execution_info()

    def collect_resource(self, resource, reason):
        if resource.url not in self._resources_urls:
            self._resources_and_reasons.append((resource, reason))
            self._resources_urls.add(resource.url)

    def collect_prev_process_and_not_primary_outputs(self, new_workflow, prev_process, reason):
        for resource in prev_process.iter_outputs():
            new_resource = new_workflow.find_resource(resource.url)
            if not (new_resource and new_resource.is_primary()):
                self.collect_resource(resource, reason)
                # Should we check for availability ?
        self._previous_processes.append(prev_process)

    def collect_process_and_available_outputs(self, workflow, process, reason):
        for resource in process.iter_outputs():
            if workflow.resource_available(resource.url):
                self.collect_resource(resource, reason)
        self._processes.append(process)

    def ensure_successful_process_validity(self, workflow, process, invalidate_urls):
        for input_resource in process.iter_inputs():
            if input_resource.is_primary():
                if self._previous_workflow:
                    if self._previous_workflow.signature(input_resource.url) != workflow.signature(input_resource.url):
                        self.collect_process_and_available_outputs(workflow, process, RESOURCE_HAS_CHANGED)
                        # All outputs have been invalidated, no need to dig further
                        return
            elif self.resource_invalid(input_resource.url):
                reason = DEPENDENCY_CHANGED.format(input_resource.url)
                self.collect_process_and_available_outputs(workflow, process, reason)
                # All outputs have been invalidated, no need to dig further
                return
        for output_resource in process.iter_outputs():
            print output_resource.url
            if output_resource.url in invalidate_urls:
                print output_resource.url
                self.collect_resource(output_resource, USER_REQUEST)
                reason = BROTHER_INVALID.format(output_resource.url)
                self.collect_process_and_available_outputs(workflow, process, reason)
                # All outputs have been invalidated, no need to dig further
                return
            elif not workflow.resource_available(output_resource.url):
                reason = BROTHER_MISSING.format(output_resource.url)
                self.collect_process_and_available_outputs(workflow, process, reason)
                # All outputs have been invalidated, no need to dig further
                return
            # Could check for integrity here

    def ensure_process_validity(self, workflow, process, invalidate_urls):
        if not process.start:
            # Process hasn't run yet. So it can't produce valid outputs
            for resource in process.iter_outputs():
                if workflow.resource_available(resource.url):
                    self.collect_resource(resource, RESOURCE_NOT_CREATED_BY_TUTTLE)
        else:
            if process.success is False:
                # Process has failed. So it can't have produced valid outputs
                for resource in process.iter_outputs():
                    if workflow.resource_available(resource.url):
                        self.collect_resource(resource, PROCESS_HAS_FAILED)
                        #  NB : we don't collect the process itself, in order to be able to check for failing processes
            else:
                # If process is in success, we need to look deeper to check if everything
                # is coherent
                self.ensure_successful_process_validity(workflow, process, invalidate_urls)

    def insure_dependency_coherence(self, workflow, invalidate_urls):
        for process in workflow.iter_processes_on_dependency_order():
            self.ensure_process_validity(workflow, process, invalidate_urls)

    def retrieve_common_processes_form_previous(self, workflow):
        if not self._previous_workflow:
            return
        for prev_process in self._previous_workflow.iter_processes():
            if prev_process.start:
                # Don't need to retreive from a process that hasn't run yet
                process = workflow.similar_process(prev_process)
                if not process:
                    self.collect_prev_process_and_not_primary_outputs(workflow, prev_process, NO_LONGER_CREATED)
                else:
                    if process.code != prev_process.code:
                        self.collect_prev_process_and_not_primary_outputs(workflow, prev_process, PROCESS_HAS_CHANGED)
                    elif process.processor.name != prev_process.processor.name:
                        self.collect_prev_process_and_not_primary_outputs(workflow, prev_process, PROCESSOR_HAS_CHANGED)
                    elif process.input_urls() != prev_process.input_urls():
                        self.collect_prev_process_and_not_primary_outputs(workflow, prev_process, NOT_SAME_INPUTS)
#                    elif process.output_urls() != prev_process.output_url():
#                        invalid_collector.collect_process_and_outputs(workflow, prev_process, NOT_SAME_OUPUTS)
#                    Should we ? Only if check-integrity
                    else:
                        # Both process are the same
                        process.retrieve_execution_info(prev_process)

    def straighten_out_availability(self, workflow):
        if self._previous_workflow:
            workflow.retrieve_signatures_new(self._previous_workflow)
        workflow.clear_availability(self.iter_urls())
        workflow.fill_missing_availability()


def prep_for_invalidation(workflow, prev_workflow, invalidate_urls):
    inv_collector = InvalidCollector(prev_workflow)
    inv_collector.retrieve_common_processes_form_previous(workflow)
    # workflow contains execution info based on what happened in previous
    inv_collector.insure_dependency_coherence(workflow, invalidate_urls)
    return inv_collector
