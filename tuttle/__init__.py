# -*- coding: utf8 -*-
from tuttle import workflow

__version__ = '0.1'

from error import TuttleError
from project_parser import ProjectParser
from workflow import Workflow


NOT_CREATED_BY_TUTTLE = "The existing resource has not been created by tuttle"
DEPENDENCY_CHANGED = "Resource depends on another resource that have changed"


class InvalidResourceCollector():
    def __init__(self):
        self.res_and_reason = []

    def collect(self, l):
        self.res_and_reason += l

    def collect_with_reason(self, list_of_resources, reason):
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
                inv_collector.collect_with_reason(resultant_from_dif, DEPENDENCY_CHANGED)
                ignore_resources = [resource for resource, _ in different] + resultant_from_dif
                workflow.retrieve_execution_info(previous_workflow, ignore_resources)
                workflow.retrieve_fingerprints(previous_workflow, ignore_resources)

            modified_primary_resources = workflow.update_primary_resource_fingerprints()
            resultant_from_modif = workflow.dependant_resources(modified_primary_resources)
            inv_collector.collect_with_reason(resultant_from_modif, DEPENDENCY_CHANGED)

            not_created = workflow.resources_not_created_by_tuttle()
            inv_collector.collect_with_reason(not_created, NOT_CREATED_BY_TUTTLE)
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
