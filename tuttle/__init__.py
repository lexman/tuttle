# -*- coding: utf8 -*-
from itertools import chain
from tuttle import workflow
from tuttle.invalidation import InvalidResourceCollector
from error import TuttleError
from project_parser import ProjectParser
from tuttle.project_parser import WorkflowError
from workflow import Workflow


version = '0.1-rc0'
__version__ = '0.1-rc0'


NOT_CREATED_BY_TUTTLE = "The existing resource has not been created by tuttle"


def parse_project(tuttlefile):
    pp = ProjectParser()
    workflow = pp.parse_and_check_file(tuttlefile)
    workflow.static_check_processes()
    return workflow


def run(workflow):
    missing = workflow.missing_inputs()
    if missing:
        error_msg = "Missing the following resources to launch the workflow :\n"
        for mis in missing:
            error_msg += "* {}\n".format(mis.url)
        raise TuttleError(error_msg)
    failing_process = workflow.pick_a_failing_process()
    if failing_process:
        raise TuttleError("Workflow already failed on process '{}'. Fix the process and run tuttle again".
                          format(failing_process.id))
    nb_process_run = workflow.run()
    return nb_process_run


def parse_invalidate_and_run(tuttlefile):
        try:
            workflow = parse_project(tuttlefile)
            previous_workflow = Workflow.load()

            inv_collector = InvalidResourceCollector()
            if previous_workflow:
                workflow.retrieve_execution_info(previous_workflow)
                workflow.retrieve_signatures(previous_workflow)
                different_res = previous_workflow.resources_not_created_the_same_way(workflow)
                inv_collector.collect_with_dependencies(different_res, previous_workflow)

            modified_primary_resources = workflow.update_primary_resource_signatures()
            inv_collector.collect_dependencies_only(modified_primary_resources, workflow)
            not_created = workflow.resources_not_created_by_tuttle()
            inv_collector.collect_resources(not_created, NOT_CREATED_BY_TUTTLE)

            workflow.reset_process_exec_info(inv_collector.resources())
            inv_collector.display()
            inv_collector.remove_resources()
            workflow.create_reports()

            nb_process_run = run(workflow)
            if nb_process_run == 0:
                print("Everything up to date")

        except TuttleError as e:
            print(e)
            return 2
        return 0


def invalidate_resources(tuttlefile, urls):
    previous_workflow = Workflow.load()
    if previous_workflow is None:
        print("Nothing to invalidate : tuttle has not been run yet, so it has not produced anything")
        return 2
    print("Invalidate")
    print("'* file://B")
    return 0
