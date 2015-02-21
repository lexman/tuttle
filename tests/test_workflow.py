#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nose.tools import *
from tuttle.workflow import *
from test_project_parser import ProjectParser
from os import path


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

file://file3 <- file://file2
""")
        workflow2 = self.get_workflow(
            """file://file3 <- file://file1
""")

        invalid = workflow1.resources_not_created_the_same_way(workflow2)
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

