#!/usr/bin/env python
# -*- coding: ascii -*-

__version__ = '0.1'

from project_parser import ProjectParser, ParsingError
from workflow import Workflow
from tuttle.workflow import ExecutionError


def prepare_workflow(tuttlefile):
    pp = ProjectParser()
    try:
        workflow = pp.parse_file(tuttlefile)
    except ParsingError as e:
        print e
        return
    return workflow


def abort_if_workflow_inconsistent(workflow):
    """ Check consistency of the workflow and display needed error messages.

    :param workflow:
    :return: False if workflow is correct, True if workflow is inconsistent
    """
    missing = workflow.missing_inputs()
    if missing:
        error_msg = "Missing the following resources to launch the workflow :\n"
        for mis in missing:
            error_msg += "* {}\n".format(mis.url)
        print error_msg
        return True
    return False


def abort_if_already_failed(workflow):
    """ Check weather a provious process already failled and has not changed.

    :param workflow:
    :return: False if workflow is correct, True if workflow is inconsistent
    """
    for process in workflow.processes:
        if process.end is not None and process.return_code != 0:
            print "Workflow already failed on process '{}'. Fix the process and run tuttle again".format(process.id())
            return True
    return False


def invalidate_previous(workflow, previous_workflow):
    to_invalidate = previous_workflow.resources_to_invalidate(workflow)
    if to_invalidate:
        print "The following resources are not valid any more :"
        for resource, reason in to_invalidate:
            print "* {} - {}".format(resource.url, reason)
    return to_invalidate


def run_workflow(workflow):
    """ Runs all the needed processes in a workflow
    :param workflow: Workflow
    :return:
    """
    workflow.prepare()
    workflow.create_reports()
    workflow.run()


def run_tuttlefile(tuttlefile_path):
        workflow = prepare_workflow(tuttlefile_path)
        if not workflow:
            return
        if abort_if_workflow_inconsistent(workflow):
            return
        previous_workflow = Workflow.load()
        if previous_workflow is not None:
            invalidated_resources = invalidate_previous(workflow, previous_workflow)
            workflow.retrieve_execution_info(previous_workflow, invalidated_resources)
            if abort_if_already_failed(workflow):
                return 2
            # actual invalidation goes here
        try:
            run_workflow(workflow)
        except ExecutionError:
            return 2
        return 0
