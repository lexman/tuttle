# -*- coding: utf8 -*-

from tuttle import workflow
from tuttle.invalidation import InvalidResourceCollector
from error import TuttleError
from project_parser import ProjectParser
from tuttle.project_parser import WorkflowError, ParsingError
from tuttle.workflow_builder import WorkflowBuilder
from workflow import Workflow


version = '0.1rc7'
__version__ = '0.1rc7'


NOT_PRODUCED_BY_TUTTLE = "The existing resource has not been produced by tuttle"
USER_REQUEST = "User request"
PROCESS_HAS_FAILED = "The resource has been produced by a failing process"

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
        msg = "Workflow already failed on process '{}'. Fix the process and run tuttle again.".format(failing_process.id)
        an_output = failing_process.pick_an_output()
        if an_output:
              msg += "\n\nIf failure has been caused by an external factor like a connection breakdown, " \
                     'use "tuttle invalidate" to reset execution then "tuttle run" again.'
        raise TuttleError(msg)
    nb_process_run = workflow.run()
    return nb_process_run


def parse_invalidate_and_run(tuttlefile, threshold=-1):
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
            inv_collector.collect_resources(not_created, NOT_PRODUCED_BY_TUTTLE)

            workflow.reset_process_exec_info(inv_collector.urls())
            inv_collector.warn_and_remove(threshold)
            workflow.create_reports()

            nb_process_run = run(workflow)
            if nb_process_run == 0:
                print("Nothing to do")
            else:
                print("====")
                print("Done")

        except TuttleError as e:
            print(e)
            return 2
        return 0

def get_resources(urls):
    result = []
    pb = WorkflowBuilder()
    for url in urls:
        resource = pb.build_resource(url)
        if resource is None:
            print("Tuttle cannot understand '{}' as a valid resource url".format(url))
            return False
        result.append(resource)
    return result


def invalidate_resources(tuttlefile, urls, threshold=-1):
    resources = get_resources(urls)
    if resources is False:
        return 2
    previous_workflow = Workflow.load()
    if previous_workflow is None:
        print("Tuttle has not run yet ! It has produced nothing, so there is nothing to invalidate.")
        return 2
    try:
        workflow = parse_project(tuttlefile)
    except TuttleError as e:
        print("Invalidation has failed because tuttlefile is has errors (a valid project is needed for "
              "clean invalidation) :")
        print(e)
        return 2

    inv_collector = InvalidResourceCollector()
    workflow.retrieve_execution_info(previous_workflow)
    workflow.retrieve_signatures(previous_workflow)
    different_res = previous_workflow.resources_not_created_the_same_way(workflow)
    inv_collector.collect_with_dependencies(different_res, previous_workflow)
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
    if inv_collector.urls():
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
