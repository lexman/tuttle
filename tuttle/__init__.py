# -*- coding: utf8 -*-
from tuttle import workflow

__version__ = '0.1'

from project_parser import ProjectParser, ParsingError, WorkflowError
from workflow import Workflow
from tuttle.workflow import ExecutionError


def invalidate_previous(workflow, previous_workflow):
    to_invalidate = previous_workflow.resources_to_invalidate(workflow)
    if to_invalidate:
        print "The following resources are not valid any more :"
        for resource, reason in to_invalidate:
            print "* {} - {}".format(resource.url, reason)
    return to_invalidate


def invalidate_not_created(workflow):
    to_invalidate = workflow.resources_not_created_by_tuttle()
    if to_invalidate:
        print "The following resources are not reliable because they were not created by tuttle  :"
        for resource, reason in to_invalidate:
            print "* {}".format(resource.url)
    return to_invalidate


def parse_invalidate_and_run(tuttlefile):
        try:
            pp = ProjectParser()
            workflow = pp.parse_and_check_file(tuttlefile)
        except ParsingError as e:
            print e
            return 2
        # Maybe missing resource code should be in parsing
        # As well as cyclic dependencies check
        previous_workflow = Workflow.load()
        if previous_workflow is not None:
            invalidated_resources = invalidate_previous(workflow, previous_workflow)
            workflow.retrieve_execution_info(previous_workflow, invalidated_resources)
            for process in workflow.processes:
                if process.end is not None and process.return_code != 0:
                    print "Workflow already failed on process '{}'. Fix the process and run tuttle again".format(process.id())
                    return 2
        invalidate_not_created(workflow)
        # actual invalidation goes here
        try:
            workflow.prepare_execution()
            workflow.create_reports()
            workflow.run()
        except ExecutionError:
            return 2
        return 0
