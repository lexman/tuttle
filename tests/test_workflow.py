#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nose.tools import *
from shutil import rmtree
from tests.functional_tests import isolate
from tuttle import workflow
from tuttle.workflow import *
from test_project_parser import ProjectParser
from os import path, remove, listdir, getcwd


class TestWorkflow():

    def test_missing_inputs(self):
        """Test the list of missing inputs"""
        pp = ProjectParser()
        project = """file://result <- file://file1, file://README.txt"""
        pp.set_project(project)
        workflow = pp.parse_project()
        missing = workflow.missing_inputs()
        assert len(missing) == 1
        assert missing[0].url == "file://file1"

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

    def test_invalidate_code_change(self):
        """ Should invalidate a resource if the code creating it changes
        """
        workflow1 = self.get_workflow(
            """file://result <- file://file1
        Initial code
""")
        workflow2 = self.get_workflow(
            """file://result <- file://file1
        Updated code
""")
        invalid = workflow1.resources_not_created_the_same_way(workflow2)
        assert len(invalid) == 1
        (resource, invalidation_reason) = invalid[0]
        assert resource.url == "file://result"
        assert invalidation_reason._reason == InvalidationReason.PROCESS_CHANGED

    def test_invalidate_removed_resource(self):
        """ Should invalidate a resource if it is not created anymore
        """
        workflow1 = self.get_workflow(
            """file://file2 <- file://file1

file://file3 <- file://file1
""")
        workflow2 = self.get_workflow(
            """file://file3 <- file://file1
""")

        invalid = workflow1.resources_not_created_the_same_way(workflow2)
        print invalid
        assert len(invalid) == 1
        (resource, invalidation_reason) = invalid[0]
        assert resource.url == "file://file2"
        assert invalidation_reason._reason == InvalidationReason.NO_LONGER_CREATED

    def test_invalidate_if_resource_dependency_change(self):
        """ Should invalidate a resource if it does not depend on the same resource anymore
        """
        workflow1 = self.get_workflow(
            """file://result <- file://file1
        Some code
""")
        workflow2 = self.get_workflow(
            """file://result <- file://file2
        Some code
""")
        invalid = workflow1.resources_not_created_the_same_way(workflow2)
        assert len(invalid) == 1
        (resource, invalidation_reason) = invalid[0]
        assert resource.url == "file://result"
        assert invalidation_reason._reason == InvalidationReason.NOT_SAME_INPUTS

    def test_invalidation_in_cascade(self):
        """ When a resource is invalidated all resulting resources should be invalidated too
        """
        workflow1 = self.get_workflow(
            """file://file2 <- file://file1
            Original code

file://file3 <- file://file2""")
        workflow2 = self.get_workflow(
            """file://file2 <- file://file1
            Updated code

file://file3 <- file://file2""")
        print(workflow1.resources)
        print(workflow1.processes)
        invalid = workflow1.resources_to_invalidate(workflow2)
        print invalid
        print workflow1.resources['file://file2']
        assert len(invalid) == 2
        (resource, invalidation_reason) = invalid[0]
        assert resource.url == "file://file2"
        assert invalidation_reason._reason == InvalidationReason.PROCESS_CHANGED

    def test_compute_dependencies(self):
        """ Every resource should know the processes dependant from it """
        workflow = self.get_workflow(
            """file://file2 <- file://file1
            Original code

file://file3 <- file://file1

""")
        workflow.compute_dependencies()
        assert workflow.resources['file://file1'].dependant_processes == [workflow.processes[0], workflow.processes[1]]

    @isolate
    def test_run_process(self):
        """
        Should run a process and update the state of the workflow
        """
        workflow = self.get_workflow(
            """file://result <- file://source
            echo result > result
            """)
        workflow.prepare_execution()
        process = workflow.processes[0]
        workflow.run_process(process, '.')
        assert path.isfile("result")
        assert path.isfile("tuttle_report.html")
        assert path.isfile(path.join(".tuttle", "last_workflow.pickle"))

    @isolate
    def test_check_process_output(self):
        """
        Should raise an exception if the output resource was not really created
        """
        workflow = self.get_workflow(
            """file://result <- file://source
            echo test
            """)
        workflow.prepare_execution()
        process = workflow.processes[0]
        try:
            workflow.run_process(process, '.')
            assert False, "Exception has not been not raised"
        except ResourceError:
            assert True

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
    def test_pick_a_process_to_run(self):
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
        p = workflow.pick_a_process_to_run()
        assert p.id() == "bat_5", p.id()
