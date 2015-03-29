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
        for process in workflow.processes:
            if process.end is not None and process.return_code != 0:
                raise AlreadyFailedError("Workflow already failed on process '{}'. Fix the process and run tuttle again".format(process.id()))
    invalid += workflow.resources_not_created_by_tuttle()
    if invalid:
        print "The following resources are not reliable because they were not created by tuttle  :"
        for resource, reason in invalid:
            print "* {} - {}".format(resource.url, reason)

def parse_invalidate_and_run(tuttlefile):
        try:
            pp = ProjectParser()
            workflow = pp.parse_and_check_file(tuttlefile)
            invalidate(workflow)
        except (ParsingError, AlreadyFailedError) as e:
            print e
            return 2
        # actual invalidation goes here
        try:
            workflow.prepare_execution()
            workflow.create_reports()
            workflow.run()
        except ExecutionError:
            return 2
        return 0
