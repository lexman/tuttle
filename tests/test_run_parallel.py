# -*- coding: utf-8 -*-
from os.path import isfile, abspath, exists

from tests.test_project_parser import ProjectParser
from tests.functional_tests import run_tuttle_file, isolate
from tuttlelib.resources import FileResource
from tuttlelib.workflow_runner import WorkflowRuner
from tuttlelib.workflow import Workflow
from time import time, sleep


class BuggyProcessor:
    # This class mus remain outside another class because it is serialized
    name = 'buggy_processor'

    def static_check(self, process):
        pass

    def run(self, process, reserved_path, log_stdout, log_stderr):
        raise Exception("Unexpected error in processor")


class BuggySignatureResource(FileResource):
    # This class mus remain outside another class because it is serialized
    scheme = 'buggy'

    def _get_path(self):
        return abspath(self.url[len("buggy://"):])

    def signature(self):
        raise Exception("Unexpected error in signature()")


class BuggyExistsResource(FileResource):
    # This class mus remain outside another class because it is serialized
    scheme = 'buggy'

    def _get_path(self):
        return abspath(self.url[len("buggy://"):])

    def exists(self):
        if exists(self._get_path()):
            raise Exception("Unexpected error in exists()")
        else:
            return False


def run_first_process(one_process_workflow, extra_processor = None, extra_resource = None):
    """ utility method to run the first process of a workflow and assert on process result """
    pp = ProjectParser()
    if extra_processor:
        # we can inject a new processor to test exceptions
        pp.wb._processors[extra_processor.name] = extra_processor

    if extra_resource:
        # we can inject a new resource to test exceptions
        pp.wb._resources_definition[extra_resource.scheme] = extra_resource

    pp.set_project(one_process_workflow)
    workflow = pp.parse_extend_and_check_project()
    process = workflow._processes[0]
    wr = WorkflowRuner(2)
    wr.init_workers()
    try:
        WorkflowRuner.prepare_and_assign_paths(process)
        wr._lt.follow_process(process.log_stdout, process.log_stderr, process.id)
        with wr._lt.trace_in_background():
            wr.start_process_in_background(process) # The function we're testing !
        timeout = time() + 0.5
        while time() < timeout and not wr._completed_processes:
            sleep(0.1)
        assert time() < timeout, "Process should have stoped now"
    finally:
        wr.terminate_workers_and_clean_subprocesses()
    return process


class TestRunParallel():

    def test_workers(self):
        """Test the flow of using workers"""
        wr = WorkflowRuner(4)
        try:
            wr.init_workers()
            assert wr.workers_available() == 4
            wr.acquire_worker()
            assert wr.workers_available() == 3
            wr.acquire_worker()
            assert wr.active_workers()
            wr.acquire_worker()
            assert wr.active_workers()
            wr.acquire_worker()
            assert not wr.active_workers()
            wr.release_worker()
            assert wr.active_workers()
            wr.release_worker()
            assert wr.workers_available() == 2
            wr.terminate_workers_and_clean_subprocesses()
        except:
            wr.terminate_workers_and_clean_subprocesses()

    def test_background_process(self):
        """ Starting a process in background should end up with the process beeing
            added to the list of completed processes"""
        first = """file://B <- file://A
            sleep 1
            echo A produces B > B
        """

        pp = ProjectParser()
        pp.set_project(first)
        workflow = pp.parse_extend_and_check_project()
        process = workflow._processes[0]

        wr = WorkflowRuner(3)
        wr.init_workers()
        try:
            wr.start_process_in_background(process)
            assert wr.active_workers()
            timeout = time() + 1.5
            while time() < timeout and not wr._completed_processes:
                sleep(0.1)
            assert time() < timeout, "Process should have stoped now"
        finally:
            wr.terminate_workers_and_clean_subprocesses()

    @isolate(['A'])
    def test_error_before_all_processes_complete(self):
        """ When a process stops in error, all running processes whould be stopped right now and declared in error """
        first = """file://B <- file://A
    sleep 1
    echo A produces B > B
    error
    
file://C <- file://A
    sleep 2
    echo A produces C > C
        """

        rcode, output = run_tuttle_file(first, nb_workers=2)
        assert rcode == 2
        assert isfile('B')
        assert not isfile('C')
        w = Workflow.load()
        p = w.find_process_that_creates("file://C")
        assert not p.success, "Process that creates C should be in error in the dump"

    def test_error_message_from_background_process(self):
        """ When the process fails, its success attribute should be false, and there should be an error message"""
        one_process_workflow = """file://B <- file://A
            error
            echo A produces B > B
        """
        process = run_first_process(one_process_workflow)
        assert process.error_message.find("Process ended with error code") >= 0, process.error_message


    @isolate(['A'])
    def test_outputs_not_created(self):
        """ When the outputs have not been created by a process, there should be an error message"""
        one_process_workflow = """file://B <- file://A
            echo A does not produce B
        """
        process = run_first_process(one_process_workflow)
        assert process.success is False, process.error_message
        assert process.error_message.find("these resources should have been created") >= 0, process.error_message
        assert process.error_message.find("* file://B") >= 0, process.error_message

    @isolate(['A'])
    def test_unexpected_error_in_processor(self):
        """ Tuttle should be protected against unexpected exceptions from the processor """

        one_process_workflow = """file://B <- file://A ! buggy_processor
            echo A does not produce B
        """
        process = run_first_process(one_process_workflow, BuggyProcessor())
        assert process.success is False, process.error_message
        assert process.error_message.find('An unexpected error have happen in tuttle processor '
                                          'buggy_processor :') >= 0, process.error_message
        assert process.error_message.find('Traceback (most recent call last):') >= 0, process.error_message
        assert process.error_message.find('raise Exception("Unexpected error in processor")') >= 0, process.error_message
        assert process.error_message.find('will not complete.') >= 0, process.error_message

    @isolate(['A'])
    def test_unexpected_error_in_signature(self):
        """ Tuttle should be protected against unexpected exceptions from resource.signature() """
        # TODO
        one_process_workflow = """buggy://B <- file://A
            echo A produces B > B
        """
        process = run_first_process(one_process_workflow, extra_resource=BuggySignatureResource)
        assert process.success is False, process.error_message
        assert process.error_message.find('An unexpected error have happen in tuttle while retrieving signature' \
                                         ) >= 0, process.error_message
        assert process.error_message.find('Traceback (most recent call last):') >= 0, process.error_message
        assert process.error_message.find('raise Exception("Unexpected error in signature()")') >= 0, process.error_message
        assert process.error_message.find('Process cannot be considered complete.') >= 0, process.error_message

    @isolate(['A'])
    def test_unexpected_error_in_exists(self):
        """ Tuttle should be protected against unexpected exceptions from resource.exists() """
        # TODO
        one_process_workflow = """buggy://B <- file://A
            echo A produces B > B
        """
        process = run_first_process(one_process_workflow, extra_resource=BuggyExistsResource)
        assert process.success is False, process.error_message
        assert process.error_message.find('An unexpected error have happen in tuttle while checking existence of '
                                          'output resources' ) >= 0, process.error_message
        assert process.error_message.find('Traceback (most recent call last):') >= 0, process.error_message
        assert process.error_message.find('raise Exception("Unexpected error in exists()")') >= 0, process.error_message
        assert process.error_message.find('Process cannot be considered complete.') >= 0, process.error_message
