# -*- coding: utf8 -*-

from tuttle import workflow
from tuttle.extend_workflow import extend_workflow
from tuttle.invalidation import InvalidResourceCollector
from error import TuttleError
from project_parser import ProjectParser
from tuttle.project_parser import WorkflowError
from tuttle.workflow_builder import WorkflowBuilder
from tuttle.workflow_runner import WorkflowRuner
from workflow import Workflow


extend_workflow = extend_workflow


NOT_PRODUCED_BY_TUTTLE = "The existing resource has not been produced by tuttle"
USER_REQUEST = "User request"
PROCESS_HAS_FAILED = "The resource has been produced by a failing process"


def load_project(tuttlefile):
    pp = ProjectParser()
    workflow = pp.parse_and_check_file(tuttlefile)
    return workflow


def print_missing_input(missing):
    error_msg = "Missing the following resources to launch the workflow :\n"
    for mis in missing:
        error_msg += "* {}\n".format(mis.url)
    print(error_msg)


def print_failing_process(failing_process):
    msg = "Workflow already failed on process '{}'. Fix the process and run tuttle again.".format(failing_process.id)
    msg += "\n\nIf failure has been caused by an external factor like a connection breakdown, " \
           'use "tuttle invalidate" to reset execution then "tuttle run" again.'
    print(msg)


def print_failures(failure_processes):
    print("Some processes have failed")
    for process in failure_processes:
        header = "== Process : {} ==".format(process.id)
        print(header)
        print(process.error_message)


def print_success():
    print("====")
    print("Done")


def print_nothing_to_do():
    print("Nothing to do")


def parse_invalidate_and_run(tuttlefile, threshold=-1):
    inv_collector = InvalidResourceCollector()
    try:
        workflow = load_project(tuttlefile)
    except TuttleError as e:
        print(e)
        return 2

    previous_workflow = Workflow.load()
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
    workflow.create_reports()
    workflow.dump()

    missing = workflow.missing_inputs()
    if missing:
        print_missing_input(missing)
        return 2

    failing_process = workflow.pick_a_failing_process()
    if failing_process:
        print_failing_process(failing_process)
        return 2

    # TODO : find a good default parameter
    wr = WorkflowRuner(4)
    success_processes, failure_processes = wr.run_parallel_workflow(workflow)
    if failure_processes:
        print_failures(failure_processes)
        return 2

    if success_processes or shrunk:
        print_success()
    else:
        print_nothing_to_do()

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
        workflow = load_project(tuttlefile)
        # TODO : add preprocessors to invalidation
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
    if inv_collector.urls() or previous_workflow.pick_a_failing_process():
        try:
            inv_collector.warn_and_remove(threshold)
        except TuttleError as e:
            print(e)
            return 2
        workflow.reset_process_exec_info(inv_collector.urls())
        for process in workflow.iter_processes():
            if not process.success:
                process.reset_execution_info()
        workflow.dump()
        workflow.create_reports()
    else:
        print("Nothing to do")
    return 0
