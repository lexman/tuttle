# -*- coding: utf-8 -*-
from os.path import isfile

from test_project_parser import ProjectParser
from tests.functional_tests import run_tuttle_file, isolate
from tuttle.workflow_runner import WorkflowRuner
from tuttle.workflow import Workflow
from time import time


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
            wr.terminate_workers()
        except:
            wr.terminate_workers()

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
        wr.run_parallel_workflow(workflow)
        wr.init_workers()
        try:
            wr.start_process_in_background(process)
            assert wr.active_workers()
            timeout = time() + 1.5
            while time() < timeout and not wr._completed_processes:
                pass
            assert time() < timeout, "Process should have stoped now"
        finally:
            wr.terminate_workers()

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

        rcode, output = run_tuttle_file(first)
        assert rcode == 2
        assert isfile('B')
        assert not isfile('C')
        w = Workflow.load()
        p = w.find_process_that_creates("file://C")
        assert not p.success, "Process that creates C should be in error in the dump"