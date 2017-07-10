# -*- coding: utf8 -*-
from itertools import chain
from tuttle.error import TuttleError


DEPENDENCY_CHANGED = "Resource depends on {} that have changed"
NOT_PRODUCED_BY_TUTTLE = "The existing resource has not been produced by tuttle"
USER_REQUEST = "User request"
PROCESS_HAS_FAILED = "The resource has been produced by a failing process"



def dependency_map(workflow):
    """ builds a map with the list of dependent process for each resource url
    """
    dependencies = {}
    for resource in workflow.iter_resources():
        dependencies[resource.url] = []
    for process in workflow.iter_processes():
        for resource in process.iter_inputs():
            dependencies[resource.url].append(process)
    return dependencies


def dependant_resources(workflow, from_resources):
    dependencies = dependency_map(workflow)
    result = []
    discovered = []
    for resource in chain(from_resources, discovered):
        for dependant_process in dependencies[resource.url]:
            for dependant_resource in dependant_process.iter_outputs():
                if dependant_resource not in result:
                    discovered.append(dependant_resource)
                    result.append((dependant_resource, resource))
    return result


class InvalidResourceCollector():
    """ This class class collects the resources to invalidate and their reason, in order to display them to the user
    and remove them all at once.
    Resources can come from several workflows (eg the current and the previous one)
    """
    def __init__(self):
        self._resources_and_reasons = []
        self._resources_urls = set()

    def urls(self):
        return self._resources_urls

    def collect_resource(self, resource, reason):
        if resource.url not in self._resources_urls:
            self._resources_and_reasons.append((resource, reason))
            self._resources_urls.add(resource.url)

    def collect_with_dependencies(self, resources_and_reasons, workflow):
        for resource, reason in resources_and_reasons:
            self.collect_resource(resource, reason)
        self.collect_dependencies_only([resource for (resource, _) in resources_and_reasons], workflow)

    def collect_dependencies_only(self, resources, workflow):
        dep_list = dependant_resources(workflow, resources)
        for child, parent in dep_list:
            reason = DEPENDENCY_CHANGED.format(parent.url)
            self.collect_resource(child, reason)

    def collect_resources(self, resources, collective_reason):
        for resource in resources:
            if resource.url not in self._resources_urls:
                self.collect_resource(resource, collective_reason)

    def not_invalidated(self, urls):
        urls_set = set(urls)
        return urls_set - self._resources_urls

    def duration(self):
        processes = {resource.creator_process for resource, _ in self._resources_and_reasons
                     if resource.creator_process is not None}
        duration_sum = sum( (process.end - process.start for process in processes if process.end is not None) )
        return int(duration_sum)

    def remove_resources(self):
        for resource, reason in self._resources_and_reasons:
            if resource.exists():
                try:
                    resource.remove()
                except Exception as e:
                    msg = 'Warning : Removing resource {} has failed. Even if the resource is still available, ' \
                          'it should not be considered valid.'.format(resource.url)
                    print(msg)

    def warn_and_remove(self, threshold):
        if self._resources_and_reasons:
            inv_duration = self.duration()
            print "The following resources are not valid any more and will be removed :"
            for resource, reason in self._resources_and_reasons:
                print("* {} - {}".format(resource.url, reason))
            if threshold > -1 and inv_duration >= threshold:
                msg = "You were about to loose {} seconds of processing time (which exceeds the {} seconds threshold). \n" \
                      "Aborting... ".format(inv_duration, threshold)
                raise TuttleError(msg)
            print("{} seconds of processing will be lost".format(inv_duration))
            self.remove_resources()


def invalidate(workflow, previous_workflow, urls, invalidate_only):
    inv_collector = InvalidResourceCollector()
    shrunk = False
    if previous_workflow:
        workflow.retrieve_execution_info(previous_workflow)
        shrunk = workflow.retrieve_signatures(previous_workflow)
        different_res = previous_workflow.resources_not_created_the_same_way(workflow)
        inv_collector.collect_with_dependencies(different_res, previous_workflow)
    if invalidate_only:
        # No need to check for failing resources if we have already
        # checked for failing process
        failed_res = workflow.failed_resources()
        inv_collector.collect_resources(failed_res, PROCESS_HAS_FAILED)
        modified_primary_resources = workflow.modified_primary_resources()
        inv_collector.collect_with_dependencies(modified_primary_resources, workflow)
        url_not_invalidated = inv_collector.not_invalidated(urls)
        to_invalidate = []
        for url in url_not_invalidated:
            resource = workflow.find_resource(url)
            if not resource:
                msg = "Ignoring {} : this resource does not belong to the workflow.".format(url)
                print(msg)
            elif not resource.exists():
                msg = "Ignoring {} : this resource has not been produced yet.".format(url)
                print(msg)
            elif resource.is_primary():
                msg = "Ignoring {} : primary resources can't be invalidated.".format(url)
                print(msg)
            else:
                to_invalidate.append(resource)
        inv_collector.collect_resources(to_invalidate, USER_REQUEST)
    else:
        modified_primary_resources = workflow.update_primary_resource_signatures()
        inv_collector.collect_dependencies_only(modified_primary_resources, workflow)
        not_created = workflow.resources_not_created_by_tuttle()
        inv_collector.collect_resources(not_created, NOT_PRODUCED_BY_TUTTLE)

    pass


def parse_invalidate_and_run(workflow, previous_workflow, threshold=-1):
    inv_collector = InvalidResourceCollector()
    shrunk = False
    if previous_workflow:
        workflow.retrieve_execution_info(previous_workflow)
        shrunk = workflow.retrieve_signatures(previous_workflow)
        different_res = previous_workflow.resources_not_created_the_same_way(workflow)
        inv_collector.collect_with_dependencies(different_res, previous_workflow)

    modified_primary_resources = workflow.update_primary_resource_signatures()
    inv_collector.collect_dependencies_only(modified_primary_resources, workflow)
    not_created = workflow.resources_not_created_by_tuttle()
    inv_collector.collect_resources(not_created, NOT_PRODUCED_BY_TUTTLE)

    workflow.reset_process_exec_info(inv_collector.urls())
    try:
        inv_collector.warn_and_remove(threshold)
    except TuttleError as e:
        print(e)
        return 2

    if success_processes or shrunk:
        print_success()
    else:
        print_nothing_to_do()

    return 0


def invalidate_resources(workflow, previous_workflow, urls, threshold=-1):
    inv_collector = InvalidResourceCollector()
    workflow.retrieve_execution_info(previous_workflow)
    workflow.retrieve_signatures(previous_workflow)
    different_res = previous_workflow.resources_not_created_the_same_way(workflow)
    inv_collector.collect_with_dependencies(different_res, previous_workflow)

    # When trying to run the process
    failed_res = workflow.failed_resources()
    inv_collector.collect_resources(failed_res, PROCESS_HAS_FAILED)

    modified_primary_resources = workflow.modified_primary_resources()
    inv_collector.collect_with_dependencies(modified_primary_resources, workflow)
    url_not_invalidated = inv_collector.not_invalidated(urls)
    to_invalidate = []
    for url in url_not_invalidated:
        resource = workflow.find_resource(url)
        if not resource:
            msg = "Ignoring {} : this resource does not belong to the workflow.".format(url)
            print(msg)
        elif not resource.exists():
            msg = "Ignoring {} : this resource has not been produced yet.".format(url)
            print(msg)
        elif resource.is_primary():
            msg = "Ignoring {} : primary resources can't be invalidated.".format(url)
            print(msg)
        else:
            to_invalidate.append(resource)
    inv_collector.collect_resources(to_invalidate, USER_REQUEST)
    inv_collector.collect_dependencies_only(to_invalidate, workflow)
    if inv_collector.urls() or previous_workflow.pick_a_failing_process():
        try:
            inv_collector.warn_and_remove(threshold)
        except TuttleError as e:
            print(e)
            return 2
        workflow.reset_process_exec_info(inv_collector.urls())
        workflow.dump()
        workflow.create_reports()
    else:
        print("Nothing to do")
    return 0
