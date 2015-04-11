# -*- coding: utf8 -*-
from tuttle.project_parser import ProjectParser

from tuttle.resources import HTTPResource


class TestHttpResource():

    def test_real_resource_exists(self):
        """A real resource should exist"""
        # TODO : change this when tuttle has its site... If it can handle the load...
        # Or by a local http server
        res = HTTPResource("http://www.google.com/")
        assert res.exists()

    def test_fictive_resource_exists(self):
        """A real resource should exist"""
        res = HTTPResource("http://www.example.com/tuttle")
        assert not res.exists()

    def test_http_resource_in_workflow(self):
        """An HTTP resource should be allowed in a workflow"""
        pp = ProjectParser()
        project = "file://result <- http://www.google.com/"
        pp.set_project(project)
        workflow = pp.parse_project()
        assert len(workflow.processes) == 1
        inputs = [res for res in workflow.processes[0].iter_inputs()]
        assert len(inputs) == 1
