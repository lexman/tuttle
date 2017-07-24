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

    def nothing_to_invalidate(self):
        return self._resources_urls and self._previous_processes and self._processes

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

    def remove_resources(self):
        for resource, reason in self._resources_and_reasons:
            if resource.exists():  # TODO : availibility
                # Are we shure we're not trying to remove an unavailable resource ?
                # If so, we can remove the test
                # Maybe a resource from the previous process, that have been
                # removed from the workflow AND deleted manually ?
                try:
                    resource.remove()
                except Exception as e:
                    msg = 'Warning : Removing resource {} has failed. Even if the resource is still available, ' \
                          'it should not be considered valid.'.format(resource.url)
                    print(msg)
            # TODO remove signature

    def reset_execution_info(self, reset_failed):
        for process in self._processes:
            process.reset_execution_info()
        if reset_failed:
            pass  # TODO !

    def collect_resource(self, resource, reason):
        if resource.url not in self._resources_urls:
            self._resources_and_reasons.append((resource, reason))
            self._resources_urls.add(resource.url)

    def collect_prev_process_and_outputs(self, prev_process, reason):
        for resource in prev_process.iter_outputs():
            if resource.url not in self._resources_urls:
                # Should we check for availability ?
                self._resources_and_reasons.append((resource, reason))
                self._resources_urls.add(resource.url)
        self._previous_processes.append(prev_process)

    def collect_process_and_available_outputs(self, process, reason, resource_availability):
        for resource in process.iter_outputs():
            if resource.url not in self._resources_urls and resource.url in resource_availability:
                self._resources_and_reasons.append((resource, reason))
                self._resources_urls.add(resource.url)
        self._processes.append(process)

    def ensure_successful_process_validity(self, process, resource_availability, invalidate_urls):
        for input_resource in process.iter_inputs():
            if input_resource.is_primary():
                if self._previous_workflow.signature() != resource_availability[input_resource.url]:
                    self.collect_resource(input_resource, RESOURCE_HAS_CHANGED)
                    reason = DEPENDENCY_CHANGED.format(input_resource.url)
                    self.collect_process_and_available_outputs(process, reason, resource_availability)
                    # All outputs have been invalidated, no need to dig further
                    return
            elif self.resource_invalid(input_resource.url):
                reason = DEPENDENCY_CHANGED.format(input_resource.url)
                self.collect_process_and_available_outputs(process, reason, resource_availability)
                # All outputs have been invalidated, no need to dig further
                return
        for output_resource in process.iter_outputs():
            if output_resource.url in invalidate_urls:
                self.collect_resource(output_resource, USER_REQUEST)
                reason = BROTHER_INVALID.format(output_resource.url)
                self.collect_process_and_available_outputs(process, reason, resource_availability)
                # All outputs have been invalidated, no need to dig further
                return
            elif output_resource.url not in resource_availability:
                reason = BROTHER_MISSING.format(output_resource.url)
                self.collect_process_and_available_outputs(process, reason, resource_availability)
                # All outputs have been invalidated, no need to dig further
                return
            # Could check for integrity here

    def ensure_process_validity(self, process, resource_availability, invalidate_urls):
        if not process.start:
            # Process hasn't run yet. So it can't produce valid outputs
            for resource in process.iter_outputs():
                if resource in resource_availability:  # NOT SURE : we might forget to invalidate a dependent process
                    self.collect_resource(resource, RESOURCE_NOT_CREATED_BY_TUTTLE)
        else:
            if process.success is False:
                # Process has failed. So it can't have produced valid outputs
                for resource in process.iter_outputs():
                    if resource in resource_availability:
                        self.collect_resource(resource, PROCESS_HAS_FAILED)
            else:
                # If process is in success, we need to look deeper to check if everything
                # is coherent
                self.ensure_successful_process_validity(process, resource_availability, invalidate_urls)

    def clear_availability(self, resource_availability):
        for url in self.iter_urls():
            del resource_availability[url]

    def fill_missing_availability(self, workflow, resource_availability):
        for url in self.iter_urls():
            if resource_availability[url] is True:
                print("Filling availability for {}".format(url))
                resource = workflow.find_resource(url)
                signature = resource.signature()
                resource_availability[signature]

    def insure_dependency_coherence(self, workflow, invalidate_urls):
        resource_availability = workflow.discover_available_resources_new()  # check-integrity would get all signatures
        for process in workflow.iter_processes_on_dependency_order():
            self.ensure_process_validity(process, resource_availability, invalidate_urls)
        # Should compute signature for outputs that have been added to some processes
        # Should set signatures to the workflow, according to what will stay after invalidation
        self.clear_availability()
        self.fill_missing_availability(workflow, resource_availability)

    def retrieve_form_previous(self, workflow):
        for prev_process in self._previous_workflow.iter_processes():
            if prev_process.start:
                # Don't need to retreive from a process that hasn't run yet
                process = workflow.similar_process(prev_process)
                if not process:
                    self.collect_prev_process_and_outputs(prev_process, NO_LONGER_CREATED)
                else:
                    if process.code != prev_process.code:
                        self.collect_prev_process_and_outputs(prev_process, PROCESS_HAS_CHANGED)
                    elif process.processor.name != prev_process.processor.name:
                        self.collect_prev_process_and_outputs(prev_process, PROCESSOR_HAS_CHANGED)
                    elif process.input_urls() != prev_process.input_url():
                        self.collect_prev_process_and_outputs(prev_process, NOT_SAME_INPUTS)
#                    elif process.output_urls() != prev_process.output_url():
#                        invalid_collector.collect_process_and_outputs(prev_process, NOT_SAME_OUPUTS)
#                    Should we ? Only if check-integrity
                    else:
                        # Both process are the same
                        process.retrieve_execution_info(prev_process)


def prep_for_invalidation(workflow, prev_workflow, invalidate_urls):
    inv_collector = InvalidCollector(prev_workflow)
    inv_collector.retrieve_form_previous(workflow, prev_workflow)
    # workflow contains execution info based on what happened in previous
    inv_collector.insure_dependency_coherence(workflow, invalidate_urls)
