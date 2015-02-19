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
        assert tuttle_dir("test") == path.join(".tuttle", "test")

    def test_two_params_from_dir(self):
        assert tuttle_dir("test1", "test2") == path.join(".tuttle", "test1", "test2")
