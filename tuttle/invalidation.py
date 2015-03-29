# -*- coding: utf8 -*-


from error import TuttleError
from workflow import Workflow, InvalidationReason


class AlreadyFailedError(TuttleError):
    pass


def invalidate(workflow):
    invalid = []
    previous_workflow = Workflow.load()
    if previous_workflow is not None:
        invalid = previous_workflow.resources_to_invalidate(workflow)
        workflow.retrieve_execution_info(previous_workflow, invalid)
        failing_process = workflow.pick_a_failing_process()
        if failing_process:
            raise AlreadyFailedError("Workflow already failed on process '{}'. Fix the process and run tuttle again".
                                     format(failing_process.id()))
    invalid += workflow.resources_not_created_by_tuttle()
    if invalid:
        print "The following resources are not valid any more and will be removed :"
        for resource, reason in invalid:
            print "* {} - {}".format(resource.url, reason)
    # actual invalidation goes here
