#!/usr/bin/env python
# -*- coding: ascii -*-

__version__ = '0.1'

from project_parser import ProjectParser, ParsingError
from workflow import Workflow


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


def invalidate_previous(workflow):
    previous_workflow = Workflow.load()
    if previous_workflow is None:
        return
    to_invalidate = previous_workflow.resources_to_invalidate(workflow)
    if to_invalidate:
        print "The following resources are not valid any more :"
        for resource, reason in to_invalidate:
            print "* {} - {}".format(resource.url, reason)


def run_workflow(workflow):
    """ Runs all the needed processes in a workflow
    :param workflow: Workflow
    :return:
    """
    workflow.prepare()
    workflow.create_reports()
    workflow.run()
