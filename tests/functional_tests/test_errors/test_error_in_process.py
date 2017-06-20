# -*- coding: utf-8 -*-

import glob
from os.path import isfile
from tests.functional_tests import isolate, run_tuttle_file
from tuttle.project_parser import ProjectParser
from tuttle.workflow_runner import WorkflowRuner


class TestErrorInProcess():

    @isolate(['A'])
    def test_error_in_process(self):
        """  When a process fail, Tuttle should exit with status code 2"""
        # As in Gnu Make

        first = """file://B <- file://A
    echo A produces B
    echo B > B

file://C <- file://B
    Obvious syntax error
    echo This should not be written
    echo C > C

file://D <- file://A
    echo A produces D
    echo D > D
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 2
        assert output.find("[stderr]") >= 0, output
        assert output.find("Obvious") >= 0, output
        assert output.find("Process ended with error code 1") >= 0, output

    @isolate(['A', 'test_error_in_process.py'])
    def test_isolation_decorator(self):
        files = glob.glob("*")
        assert set(files) == set(['A', 'test_error_in_process.py']), files

    @isolate
    def test_isolation_decorator_without_args(self):
        assert True

    @isolate(['A'])
    def test_fail_if_already_failed(self):
        """  When a process fail, Tuttle should exit with status code 2"""
        # As in Gnu Make
        first = """file://B <- file://A
    echo A produces B
    echo B > B

file://C <- file://B
    error
    echo This should not be written
    echo C > C

file://D <- file://A
    echo A produces D
    echo D > D
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 2
        assert isfile('B')
        assert not isfile('C')
        assert not isfile('D')
        second = """file://B <- file://A
    echo A produces B
    echo B > B

file://C <- file://B
    error
    echo This should not be written
    echo C > C

file://D <- file://A
    echo A produces D
    echo Minor change
    echo D > D
"""
        rcode, output = run_tuttle_file(second)
        assert rcode == 2
        assert output.find("Workflow already failed") >= 0, output

    # Not sure about that
#     @isolate(['A'])
#     def test_fail_if_already_failed_even_without_outputs(self):
#         """  When a process fail, Tuttle should exit with status code 2, even if the process has no outputs"""
#         project = """file://B <- file://A
#     echo A produces B
#     echo B > B
#
# <- file://B
#     error
#     echo This should not be written
#     echo C > C
# """
#         rcode, output = run_tuttle_file(project)
#         assert rcode == 2
#         assert isfile('B')
#         assert not isfile('C')
#
#         rcode, output = run_tuttle_file(project)
#         assert rcode == 2
#         assert output.find("Workflow already failed") >= 0, output

    @isolate(['A'])
    def test_process_fail_if_output_not_created(self):
        """  If the all the outputs of a process have not been created, the process should be marked as failed
        even if no error occurred.
        Useful when displaying html report
        """

        first = """file://B <- file://A
    echo A won't produce B
"""

        pp = ProjectParser()
        pp.set_project(first)
        workflow = pp.parse_extend_and_check_project()
        try:
            WorkflowRuner.run_workflow(workflow)
            assert False, "A resource error should have been raised"
        except:
            assert True
        process = workflow._processes[0]
        assert process.success is False, "Process should be marked as failed"
