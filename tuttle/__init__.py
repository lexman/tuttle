# -*- coding: utf8 -*-
from tuttle import workflow

__version__ = '0.1'

from project_parser import ProjectParser, ParsingError, WorkflowError
from workflow import Workflow
from tuttle.workflow import ExecutionError


class AlreadyFailedError(Exception):
    pass


def invalidate(workflow):
    previous_workflow = Workflow.load()
    invalid = []
    if previous_workflow is not None:
        invalid = previous_workflow.resources_to_invalidate(workflow)
        workflow.retrieve_execution_info(previous_workflow, invalid)
        failing_process = workflow.pick_a_failing_process()
        if failing_process:
            raise AlreadyFailedError("Workflow already failed on process '{}'. Fix the process and run tuttle again".
                                     format(failing_process.id()))
    invalid += workflow.resources_not_created_by_tuttle()
    if invalid:
        print "The following resources are not reliable because they were not created by tuttle  :"
        for resource, reason in invalid:
            print "* {} - {}".format(resource.url, reason)
    # actual invalidation goes here

def parse_invalidate_and_run(tuttlefile):
        try:
            pp = ProjectParser()
            workflow = pp.parse_and_check_file(tuttlefile)
        except ParsingError as e:
            print e
            return 2
        try:
            invalidate(workflow)
        except AlreadyFailedError as e:
            print e
            return 2
        try:
            workflow.prepare_execution()
            workflow.create_reports()
            workflow.run()
        except ExecutionError as e:
            print e
            return 2
        return 0
