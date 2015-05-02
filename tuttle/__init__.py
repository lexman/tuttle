# -*- coding: utf8 -*-
from itertools import chain
from tuttle import workflow

__version__ = '0.1'

from error import TuttleError
from project_parser import ProjectParser
from workflow import Workflow


NOT_CREATED_BY_TUTTLE = "The existing resource has not been created by tuttle"


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
            inv_collector = InvalidResourceCollector()
            previous_workflow = Workflow.load()
            if previous_workflow:
                different = previous_workflow.resources_not_created_the_same_way(workflow)
                inv_collector.collect(different)
                resultant_from_dif = previous_workflow.dependant_resources([resource for (resource, _) in different])
                inv_collector.collect(resultant_from_dif)
                ignore_urls = {resource.url for resource, _ in chain(different, resultant_from_dif)}
                workflow.retrieve_execution_info(previous_workflow, ignore_urls)
                workflow.retrieve_fingerprints(previous_workflow, ignore_urls)

            modified_primary_resources = workflow.update_primary_resource_fingerprints()
            resultant_from_modif = workflow.dependant_resources(modified_primary_resources)
            inv_collector.collect(resultant_from_modif)

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
