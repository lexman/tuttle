# -*- coding: utf8 -*-
from tuttle import workflow

__version__ = '0.1'

from error import TuttleError
from project_parser import ProjectParser
from workflow import Workflow
from invalidation import invalidate


def display_invalidity(different, modified, resultant):
    print "The following resources are not valid any more and will be removed :"
    for resource, reason in different:
        print "* {} - {}".format(resource.url, reason)
    for resource in modified:
        print "* {} - This primary resource has been modified".format(resource.url)
    for resource in resultant:
        print "* {} - Resource depends on another resource that have changed".format(resource.url)


def display_invalidity2(not_created):
    for resource, reason in not_created:
        print "* {} - {}".format(resource.url, reason)


def display_invalidity_unified(invalid):
    if invalid:
        print "The following resources are not valid any more and will be removed :"
        for resource, reason in invalid:
            print "* {} - {}".format(resource.url, reason)


# TODO : should'nt we be able to know if the resource exists without asking ?
def remove_resources(to_remove):
    for resource in to_remove:
        if resource.exists():
            resource.remove()


def resources_to_remove(different, resultant):
    result = []
    for resource, _ in different:
        result.append(resource)
    for resource in resultant:
        result.append(resource)
    return result

NOT_CREATED_BY_TUTTLE = "The existing resource has not been created by tuttle"
DEPENDENCY_CHANGED = "Resource depends on another resource that have changed"


class InvalidResourceCollector():
    def __init__(self):
        self.res_and_reason = []

    def collect(self, l):
        self.res_and_reason += l

    def collect_resources_with_same_reason(self, list_of_resources, reason):
        self.res_and_reason += [(resource, reason) for resource in list_of_resources]

    def display(self):
        if self.res_and_reason:
            print "The following resources are not valid any more and will be removed :"
            for resource, reason in self.res_and_reason:
                print "* {} - {}".format(resource.url, reason)

    def remove(self):
        for resource, reason in self.res_and_reason:
            if resource.exists():
                resource.remove()


def parse_invalidate_and_run(tuttlefile):
        try:
            pp = ProjectParser()
            workflow = pp.parse_and_check_file(tuttlefile)
            workflow.pre_check_processes()
            previous_workflow = Workflow.load()
            inv_collector = InvalidResourceCollector()
            if previous_workflow is not None:
                different = previous_workflow.resources_not_created_the_same_way(workflow)
                inv_collector.collect(different)
                resultant_from_dif = previous_workflow.dependant_resources([resource for (resource, _) in different])
                inv_collector.collect_resources_with_same_reason(resultant_from_dif, DEPENDENCY_CHANGED)
                ignore_resources = [resource for resource, _ in different] + resultant_from_dif
                workflow.retrieve_execution_info2(previous_workflow, ignore_resources)

            # si une ressource était présente au dernier workflow
            # il faut vérifier si elle a changé depuis
            # sinon, il faut enregistrer sa signature
            #modified_primary_resources = workflow.update_primary_resources_signatures()
            #resultant = previous_workflow.dependant_resources(modified_primary_resources)

            not_created = workflow.resources_not_created_by_tuttle()
            inv_collector.collect_resources_with_same_reason(not_created, NOT_CREATED_BY_TUTTLE)
            inv_collector.display()
            inv_collector.remove()

            workflow.create_reports()
            failing_process = workflow.pick_a_failing_process()
            if failing_process:
                raise TuttleError("Workflow already failed on process '{}'. Fix the process and run tuttle again".
                                         format(failing_process.id))
            workflow.run()
        except TuttleError as e:
            print e
            return 2
        return 0
