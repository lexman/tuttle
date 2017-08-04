from tuttle.error import TuttleError
from tuttle.invalidation import InvalidCollector
from tuttle.project_parser import ProjectParser
from tuttle.workflow import Workflow
from tuttle.workflow_builder import WorkflowBuilder
from tuttle.workflow_runner import WorkflowRuner
from tuttle_directories import TuttleDirectories
from os.path import abspath


def load_project(tuttlefile):
    pp = ProjectParser()
    workflow = pp.parse_and_check_file(tuttlefile)
    workflow.discover_resources()
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
    print("\nSummary : {} processe(s) have failed:".format(len(failure_processes)))
    for process in failure_processes:
        header = "== Process : {} ==".format(process.id)
        print(header)
        print(process.error_message)


def report_url():
    report_path = abspath(TuttleDirectories.tuttle_dir("report.html"))
    return "file://{}".format(report_path)


def print_success():
    print("====")
    print("Done. See report at {}".format(report_url()))


def print_nothing_to_do():
    print("Nothing to do")


def print_updated():
    print("Report has been updated to reflect tuttlefile. See {}".format(report_url()))


def print_earlier_failures():
    print("Workflow has not succedded because of earlier failures.")


def print_abort_on_threshold(inv_duration, threshold):
    msg = "You were about to loose {} seconds of processing time (which exceeds the {} seconds " \
          "threshold). \nAborting... ".format(inv_duration, threshold)
    print(msg)


def print_lost_sec(inv_duration):
    print("{} seconds of processing will be lost".format(inv_duration))


def parse_invalidate_and_run(tuttlefile, threshold=-1, nb_workers=-1, keep_going=False):
    try:
        workflow = load_project(tuttlefile)
    except TuttleError as e:
        print(e)
        return 2

    missing = workflow.primary_inputs_not_available()
    if missing:
        print_missing_input(missing)
        return 2

    previous_workflow = Workflow.load()

    inv_collector = InvalidCollector(previous_workflow)
    inv_collector.retrieve_common_processes_form_previous(workflow)
    inv_collector.insure_dependency_coherence(workflow, [], False)

    inv_duration = inv_collector.duration()  # compute duration before reset
    inv_collector.reset_execution_info()  # Ensure invalid failure process are reseted

    failing_process = workflow.pick_a_failing_process()
    if failing_process and not keep_going:
        # check before invalidate
        print_failing_process(failing_process)
        return 2

    if inv_collector._resources_and_reasons:  # BETTER TEST NEEDED HERE
        inv_collector.warn_remove_resoures()
        if -1 < threshold <= inv_duration:
            print_abort_on_threshold(inv_duration, threshold)
            return 2
        else:
            print_lost_sec(inv_duration)

    # We have to remove resources, even if there is no previous workflow,
    # because of resources that may not have been produced by tuttle
    inv_collector.remove_resources(workflow)
    inv_collector.straighten_out_signatures(workflow)
    TuttleDirectories.straighten_out_process_and_logs(workflow)
    workflow.create_reports()
    workflow.dump()

    wr = WorkflowRuner(nb_workers)
    success_processes, failure_processes = wr.run_parallel_workflow(workflow, keep_going)
    if failure_processes:
        print_failures(failure_processes)
        return 2

    if success_processes:
        print_success()
        if failing_process:
            print_earlier_failures()
            return 2
    elif inv_collector.something_to_invalidate():
        print_updated()
    else:
        print_nothing_to_do()
        if failing_process:
            print_earlier_failures()
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


def filter_invalidable_urls(workflow, urls):
    """ Returns a list of url that can be invalidated and warns about illegal urls"""
    to_invalidate = []
    for url in urls:
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
            to_invalidate.append(url)
    return to_invalidate


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

    to_invalidate = filter_invalidable_urls(workflow, urls)

    inv_collector = InvalidCollector(previous_workflow)
    inv_collector.retrieve_common_processes_form_previous(workflow)
    inv_collector.insure_dependency_coherence(workflow, to_invalidate, True)

    if inv_collector.resources_to_invalidate():
        inv_collector.warn_remove_resoures()
        inv_duration = inv_collector.duration()  # compute duration before reset
        if -1 < threshold <= inv_duration:
            print_abort_on_threshold(inv_duration, threshold)
            return 2
        else:
            print_lost_sec(inv_duration)
        inv_collector.remove_resources(workflow)
        inv_collector.reset_execution_info()
        inv_collector.straighten_out_signatures(workflow)
    reseted_failures = workflow.reset_failures()
    if inv_collector.resources_to_invalidate() or reseted_failures:
        TuttleDirectories.straighten_out_process_and_logs(workflow)
        workflow.dump()
        workflow.create_reports()

    if not inv_collector.resources_to_invalidate():
        if reseted_failures or inv_collector.something_to_invalidate():
            print_updated()
        else:
            print_nothing_to_do()
    return 0
