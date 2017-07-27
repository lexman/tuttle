# -*- coding: utf-8 -*-

from tests.functional_tests import isolate, run_tuttle_file
from tuttlelib.error import TuttleError
from tuttlelib.workflow import *
from test_project_parser import ProjectParser
from os import path
from tuttlelib.workflow_runner import WorkflowRuner, tuttle_dir


class TestWorkflow():

    def test_one_param_from_dir(self):
        """Should find the right path to a file in the project directory"""
        assert tuttle_dir("test") == path.join(".tuttle", "test")

    def test_two_params_from_dir(self):
        """Should find the right path to a file in the project directory"""
        assert tuttle_dir("test1", "test2") == path.join(".tuttle", "test1", "test2")

    def get_workflow(self, project_source):
        pp = ProjectParser()
        pp.set_project(project_source)
        return pp.parse_project()

    def test_compute_dependencies(self):
        """ Every resource should know the processes dependant from it """
        workflow = self.get_workflow(
            """file://file2 <- file://file1
            Original code

file://file3 <- file://file1

""")
        workflow.compute_dependencies()
        assert workflow._resources['file://file1'].dependant_processes == [workflow._processes[0],
                                                                           workflow._processes[1]]

    @isolate
    def test_run_process(self):
        """
        Should run a process and create the expected files according to the process and to tuttle tool
        """
        workflow = self.get_workflow(
            """file://result <- file://source
            echo result > result
            """)
        process = workflow._processes[0]
        WorkflowRuner.create_tuttle_dirs()
        WorkflowRuner.prepare_and_assign_paths(process)
        process._processor.run(process, process._reserved_path, process.log_stdout, process.log_stderr)
        assert path.isfile("result")

    @isolate(['A'])
    def test_dump_and_report_workflow(self):
        """
        When a workflow is run, the report should be written and the state should be dumped, even if there is a failure
        """
        project = """file://result <- file://A
            echo result > result
            error
            """
        rcode, output = run_tuttle_file(project)
        assert rcode == 2
        assert path.isfile(path.join(".tuttle", "last_workflow.pickle"))

    @isolate(['A'])
    def test_check_process_output(self):
        """
        Should raise an exception if the output resource was not really created
        """
        workflow = self.get_workflow(
            """file://result <- file://A
            echo test
            """)
        workflow.static_check_processes()
        workflow.discover_resources()
        wr = WorkflowRuner(3)
        successes, failures = wr.run_parallel_workflow(workflow)
        assert failures
        failure = failures[0]
        assert failure.error_message.find("these resources should have been created") >= 0, failure.error_message

    @isolate(['A'])
    def test_missing_outputs(self):
        """Test the list of missing outputs"""
        pp = ProjectParser()
        project = """file://B file://C file://D  <- file://file1 file://A
            echo C > C
        """
        pp.set_project(project)
        workflow = pp.parse_project()

        process = workflow._processes[0]
        WorkflowRuner.create_tuttle_dirs()
        WorkflowRuner.prepare_and_assign_paths(process)
        process._processor.run(process, process._reserved_path, process.log_stdout, process.log_stderr)
        missing = process.missing_outputs()

        assert len(missing) == 2
        assert missing[0].url == "file://B"
        assert missing[1].url == "file://D"

    def test_check_circular_references(self):
        """
        Should return true for there are some circular references
        """
        workflow = self.get_workflow(
            """file://A <- file://B

file://B <- file://A
file://D <- file://C
            """)
        cr = workflow.circular_references()
        assert len(cr) == 2, cr

    def test_check_no_circular_references(self):
        """
        Should return true for there are some circular references
        """
        workflow = self.get_workflow(
            """file://A <- file://B

file://B <- file://C
            """)
        assert not workflow.circular_references()

    @isolate(['A'])
    def test_runnable_processes(self):
        """
        Should run a process and update the state of the workflow
        """
        workflow = self.get_workflow(
            """file://C <- file://B
            echo C > C
            echo B creates C

file://B <- file://A
            echo B > B
            echo A creates B
            """)
        workflow.discover_resources()
        processes = workflow.runnable_processes()
        assert processes, processes
        p = processes.pop()
        assert p.id.find("_5") >= 0, p.id
