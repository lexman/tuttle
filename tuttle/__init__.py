# -*- coding: utf8 -*-
from itertools import chain
from tuttle import workflow
from tuttle.invalidation import InvalidResourceCollector
from error import TuttleError
from project_parser import ProjectParser
from workflow import Workflow


__version__ = '0.1-rc0'


NOT_CREATED_BY_TUTTLE = "The existing resource has not been created by tuttle"


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
