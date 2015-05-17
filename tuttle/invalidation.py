# -*- coding: utf8 -*-
from itertools import chain
from tuttle.error import TuttleError


DEPENDENCY_CHANGED = "Resource depends on {} that have changed"


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

    def resources(self):
        for resource, _ in self._resources_and_reasons:
            yield resource

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
                resource.remove()

    def warn_and_remove(self, threshold):
        if self._resources_and_reasons:
            inv_duration = self.duration()
            print "The following resources are not valid any more and will be removed :"
            for resource, reason in self._resources_and_reasons:
                print "* {} - {}".format(resource.url, reason)
            if threshold > -1 and inv_duration >= threshold:
                msg = "You were about to loose {} seconds of processing time (which exceeds the {} seconds threshold). \n" \
                      "Aborting... ".format(inv_duration, threshold)
                raise TuttleError(msg)
            print "{} seconds of processing will be lost".format(inv_duration)
            self.remove_resources()
