#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nose.tools import *
from tuttle.workflow import *
from test_project_parser import ProjectParser


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
