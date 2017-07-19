from tuttle import load_project, print_missing_input, print_failing_process, print_failures, print_success, \
    print_nothing_to_do, NOT_PRODUCED_BY_TUTTLE, PROCESS_HAS_FAILED, USER_REQUEST, print_updated
from tuttle.error import TuttleError
from tuttle.invalidation import InvalidResourceCollector
from tuttle.workflow import Workflow
from tuttle.workflow_builder import WorkflowBuilder
from tuttle.workflow_runner import WorkflowRuner


def parse_invalidate_and_run(tuttlefile, threshold=-1):
    try:
        workflow = load_project(tuttlefile)
    except TuttleError as e:
        print(e)
        return 2

    workflow.discover_resources()

    missing = workflow.primary_inputs_not_available()
    if missing:
        print_missing_input(missing)
        return 2

    previous_workflow = Workflow.load()
    inv_collector, workflow_changed = prepare_workflow_for_invalidation(workflow, previous_workflow, [], False)
    #if previous_workflow:
    #    workflow.reset_modified_outputless_processes(previous_workflow)
    workflow.reset_process_exec_info(inv_collector.urls())

    failing_process = workflow.pick_a_failing_process()
    if failing_process:
        # check before invalidate
        print_failing_process(failing_process)
        return 2

    if inv_collector.warn_and_abort_on_threshold(threshold):
        return 2
    # We have to remove resources, even if there is no previous workflow,
    # because of resources that may not have been produced by tuttle
    inv_collector.remove_resources()
    workflow.create_reports()
    workflow.dump()

    # TODO : find a good default parameter
    wr = WorkflowRuner(4)
    success_processes, failure_processes = wr.run_parallel_workflow(workflow)
    if failure_processes:
        print_failures(failure_processes)
        return 2

    if success_processes or workflow_changed:
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

    workflow.discover_resources()
    inv_collector, workflow_changed = prepare_workflow_for_invalidation(workflow, previous_workflow, urls, True)

    reseted = workflow.reset_failing_outputless_process_exec_info()
    workflow_changed = workflow_changed or reseted
    if inv_collector.urls():
        if inv_collector.warn_and_abort_on_threshold(threshold):
            return 2
        inv_collector.remove_resources()
    workflow.reset_process_exec_info(
            inv_collector.urls())  # Fortunately, duration will be computed from the previous processes
    if previous_workflow.pick_a_failing_process() :
        reset_failing = workflow.reset_failing_outputless_process_exec_info()
        workflow_changed = workflow_changed or reset_failing
    if not inv_collector.urls() and workflow_changed:
        print_updated()

    if inv_collector.urls() or workflow_changed:
        workflow.dump()
        workflow.create_reports()
    else:
        print_nothing_to_do()
    return 0


def prepare_workflow_for_run_invalidation(workflow, previous_workflow):
    inv_collector = InvalidResourceCollector()
    workflow_changed = False
    if previous_workflow:
        different_res = previous_workflow.resources_not_created_the_same_way(workflow)
        inv_collector.collect_with_dependencies(different_res, previous_workflow)
        modified_primary_resources = workflow.modified_resources(previous_workflow, only_primary=True)
        inv_collector.collect_dependencies_only(modified_primary_resources, workflow)
    not_created = workflow.resources_not_created_by_tuttle_new(previous_workflow)
    inv_collector.collect_resources(not_created, NOT_PRODUCED_BY_TUTTLE)
    if previous_workflow:
        workflow_changed = workflow.retrieve_signatures_new(previous_workflow)  # In advanced check, we should need only shrunk
        workflow.retrieve_execution_info_new(previous_workflow)

        incoherent = workflow.incoherent_outputs_from_successfull_processes()
        inv_collector.collect_with_dependencies(incoherent, previous_workflow)
    return inv_collector, workflow_changed


def prepare_workflow_for_invalidation(workflow, previous_workflow, urls, invalidate_failed_resources):
    inv_collector = InvalidResourceCollector()
    workflow_changed = False
    if previous_workflow:
        different_res = previous_workflow.resources_not_created_the_same_way(workflow)
        inv_collector.collect_with_dependencies(different_res, previous_workflow)
        modified_primary_resources = workflow.modified_resources(previous_workflow, only_primary=True)
        inv_collector.collect_dependencies_only(modified_primary_resources, workflow)

    # Should be ok for invalidate
    not_created = workflow.resources_not_created_by_tuttle_new(previous_workflow)
    inv_collector.collect_resources(not_created, NOT_PRODUCED_BY_TUTTLE)

    if previous_workflow:
        shrunk = workflow.retrieve_signatures_new(previous_workflow)  # In advanced check, we should need only shrunk
        workflow_changed = workflow_changed or shrunk
        workflow.retrieve_execution_info_new(previous_workflow)

        incoherent = workflow.incoherent_outputs_from_successfull_processes()
        inv_collector.collect_with_dependencies(incoherent, previous_workflow)
        reseted = workflow.reset_modified_outputless_processes(previous_workflow)
        workflow_changed = workflow_changed or reseted
    if invalidate_failed_resources:
        failed_res = workflow.failed_resources()
        inv_collector.collect_resources(failed_res, PROCESS_HAS_FAILED)
    if urls:
        url_not_invalidated = inv_collector.not_invalidated(urls)
        to_invalidate = []
        for url in url_not_invalidated:
            resource = workflow.find_resource(url)
            if not resource:
                msg = "Ignoring {} : this resource does not belong to the workflow.".format(url)
                print(msg)
            elif not workflow.resource_available(url):
                msg = "Ignoring {} : this resource has not been produced yet.".format(url)
                print(msg)
            elif resource.is_primary():
                msg = "Ignoring {} : primary resources can't be invalidated.".format(url)
                print(msg)
            else:
                to_invalidate.append(resource)
        inv_collector.collect_resources(to_invalidate, USER_REQUEST)
        inv_collector.collect_dependencies_only(to_invalidate, workflow)

    return inv_collector, workflow_changed


def prepare_workflow_for_invalidate_invalidation(workflow, urls, previous_workflow):
    inv_collector = InvalidResourceCollector()

    different_res = previous_workflow.resources_not_created_the_same_way(workflow)
    inv_collector.collect_with_dependencies(different_res, previous_workflow)
    modified_primary_resources = workflow.modified_resources(previous_workflow, only_primary=True)
    inv_collector.collect_dependencies_only(modified_primary_resources, workflow)

    workflow.retrieve_signatures_new(previous_workflow)  # In advanced check, we should not need that
    workflow.retrieve_execution_info_new(previous_workflow)
    failed_res = workflow.failed_resources()
    inv_collector.collect_resources(failed_res, PROCESS_HAS_FAILED)
    url_not_invalidated = inv_collector.not_invalidated(urls)
    to_invalidate = []
    for url in url_not_invalidated:
        resource = workflow.find_resource(url)
        if not resource:
            msg = "Ignoring {} : this resource does not belong to the workflow.".format(url)
            print(msg)
        elif not workflow.resource_available(url):
            msg = "Ignoring {} : this resource has not been produced yet.".format(url)
            print(msg)
        elif resource.is_primary():
            msg = "Ignoring {} : primary resources can't be invalidated.".format(url)
            print(msg)
        else:
            to_invalidate.append(resource)
    inv_collector.collect_resources(to_invalidate, USER_REQUEST)
    inv_collector.collect_dependencies_only(to_invalidate, workflow)
    return inv_collector
