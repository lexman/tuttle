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


def parse_invalidate_and_run(tuttlefile):
        try:
            pp = ProjectParser()
            workflow = pp.parse_and_check_file(tuttlefile)
            workflow.pre_check_processes()
            previous_workflow = Workflow.load()
            if previous_workflow is not None:
                different = previous_workflow.resources_not_created_the_same_way(workflow)
                resultant = previous_workflow.dependant_resources([resource for (resource, _) in different])
                display_invalidity(different, [], resultant)
                to_remove = resources_to_remove(different, resultant)
                remove_resources(to_remove)
                remove_urls = [resource.url for resource in to_remove]
                workflow.retrieve_execution_info2(previous_workflow, remove_urls)

            not_created = workflow.resources_not_created_by_tuttle()
            display_invalidity2(not_created)
            remove_resources([res for res, _ in not_created])

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
