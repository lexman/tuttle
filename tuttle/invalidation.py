# -*- coding: utf8 -*-
from itertools import chain

NOT_PRODUCED_BY_TUTTLE = "The existing resource has not been produced by tuttle"
USER_REQUEST = "User request"
PROCESS_HAS_FAILED = "The resource has been produced by a failing process"
NO_LONGER_CREATED = "Resource no longer created by the newer process"
NOT_SAME_INPUTS = "Resource was created with different inputs"
PROCESS_HAS_CHANGED = "Process code has changed"
PROCESSOR_HAS_CHANGED = "Processor has changed"
RESOURCE_HAS_CHANGED = "Resource depends on primary resource {} which has changed"
RESOURCE_INTEGRITY = "Resource has changed outside of tuttle"
NOT_SAME_OUTPUTS = "Other outputs from same process have changed"
DEPENDENCY_CHANGED = "Resource depends on {} which is not valid anymore"
BROTHER_INVALID = "Resource is created along with {} that is invalid"
BROTHER_MISSING = "Resource is created along with {} that is missing"
BROTHER_INTEGRITY = "Resource is created along with {} that have changed outside of tuttle"

# Is it a subscase of NOT_PRODUCED_BY_TUTTLE ?
MUST_CREATE_RESOURCE = "The former primary resource has to be created by tuttle"


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

    def warn_remove_resoures(self):
        print("The following resources are not valid any more and will be removed :")
        for resource, reason in self._resources_and_reasons:
            print("* {} - {}".format(resource.url, reason))

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

    def ensure_complete_process_validity(self, workflow, process, invalidate_urls, check_integrity):
        for input_resource in process.iter_inputs():
            if input_resource.is_primary():
                if self._previous_workflow:
                    if self._previous_workflow.signature(input_resource.url) != workflow.signature(input_resource.url):
                        reason = RESOURCE_HAS_CHANGED.format(input_resource.url)
                        self.collect_process_and_available_outputs(workflow, process, reason)
                        # All outputs have been invalidated, no need to dig further
                        return
            elif self.resource_invalid(input_resource.url):
                reason = DEPENDENCY_CHANGED.format(input_resource.url)
                self.collect_process_and_available_outputs(workflow, process, reason)
                # All outputs have been invalidated, no need to dig further
                return
        if process.success is False:
            # Only inputs can invalidate a failing process
            return
        for output_resource in process.iter_outputs():
            if output_resource.url in invalidate_urls:
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
            elif check_integrity and not output_resource.is_primary() and \
                    self._previous_workflow.signature(output_resource.url) != workflow.signature(output_resource.url):
                self.collect_resource(output_resource, RESOURCE_INTEGRITY)
                reason = BROTHER_INTEGRITY.format(output_resource.url)
                self.collect_process_and_available_outputs(workflow, process, reason)
                # All outputs have been invalidated, no need to dig further
                return
            # Could check for integrity here

    def ensure_process_validity(self, workflow, process, invalidate_urls, invalidate_failures, check_integrity):
        if not process.start:
            # Process hasn't run yet. So it can't have produced valid outputs
            for resource in process.iter_outputs():
                if workflow.resource_available(resource.url):
                    self.collect_resource(resource, NOT_PRODUCED_BY_TUTTLE)
        else:
            # If process has run, we need to look deeper to check if everything is coherent
            self.ensure_complete_process_validity(workflow, process, invalidate_urls, check_integrity)

            if invalidate_failures and process.success is False:
                # Process has failed. So it can't have produced valid outputs
                for resource in process.iter_outputs():
                    if workflow.resource_available(resource.url):
                        self.collect_resource(resource, PROCESS_HAS_FAILED)
                        #  NB : we don't collect the process itself, in order to be able to check for failing processes

    def insure_dependency_coherence(self, workflow, invalidate_urls, invalidate_failures, check_integrity):
        # Take care of failing processes
        for process in workflow.iter_processes_on_dependency_order():
            self.ensure_process_validity(workflow, process, invalidate_urls, invalidate_failures, check_integrity)

    def retrieve_common_processes_form_previous(self, workflow):
        if not self._previous_workflow:
            return
        for prev_process in self._previous_workflow.iter_processes():
            if prev_process.start:
                # Don't need to retrieve from a process that hasn't run yet
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
                    elif process.output_urls() != prev_process.output_urls():
                        self.collect_prev_process_and_not_primary_outputs(workflow, prev_process, NOT_SAME_OUTPUTS)
                        # We could be less restrictive : if someone adds an output because he discovered his process
                        # produces logs, we'd like to add them to the project without reprocessing
                        # At the condition that no process uses this new output
#                       What about check-integrity too ?
                    else:
                        # Both process are the same
                        process.retrieve_execution_info(prev_process)

    def straighten_out_signatures(self, workflow):
        if self._previous_workflow:
            workflow.retrieve_signatures(self._previous_workflow)
        workflow.clear_signatures(self.iter_urls())
        failed = {resource.url for resource in workflow.iter_resources()
                  if resource.creator_process and resource.creator_process.success is False}
        workflow.clear_signatures(failed)
        # Assert straight :
        for resource in workflow.iter_resources():
            assert workflow.signature(resource.url) != "DISCOVERED", resource.url
        # Not needed unless we make adding outputs more flexible
        # workflow.fill_missing_availability()
