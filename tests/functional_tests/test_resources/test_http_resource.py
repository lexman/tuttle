# -*- coding: utf8 -*-
from tuttle.project_parser import ProjectParser

from tuttle.resources import HTTPResource


class TestHttpResource():

    def test_real_resource_exists(self):
        """A real resource should exist"""
        # TODO : Whenge this when tuttle has its site... If it can handle the load...
        res = HTTPResource("http://www.google.com/")
        assert res.exists()

    def test_fictive_resource_exists(self):
        """A real resource should exist"""
        res = HTTPResource("http://www.example.com/tuttle")
        assert not res.exists()

    def test_http_resource_in_workflos(self):
        """An HTTP resource should be usable in a workflow"""
        pp = ProjectParser()
        project = "file://result <- http://www.google.com/"
        pp.set_project(project)
        workflow = pp.parse_project()
        assert len(workflow.processes) == 1
        assert len(workflow.processes[0].inputs) == 1
        assert len(workflow.processes[0].outputs) == 1
