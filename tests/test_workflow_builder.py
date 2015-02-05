#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nose.tools import *
from tuttle.workflow_builder import *


class TestProjectBuilder():

    def test_extract_scheme(self):
        """A file ressource should return a file protocol"""
        wb = WorkflowBuilder()
        url = "file://test.csv"
        assert wb.extract_scheme(url) == "file"

    def test_cant_extract_scheme(self):
        """Should return False if no protocol is present"""
        wb = WorkflowBuilder()
        url = "LoremIpsum"
        assert wb.extract_scheme(url) is False

    def test_build_file_ressource(self):
        """Build a file resource according to a file: uri"""
        wb = WorkflowBuilder()
        url = "file://test.csv"
        resource = wb.build_resource(url)
        assert isinstance(resource, FileResource)

    def test_build_ressource_with_unknown_scheme(self):
        """Building a resource with an unknown protocol should return None"""
        wb = WorkflowBuilder()
        url = "unknown://test.csv"
        resource = wb.build_resource(url)
        assert resource is None

    def test_build_ressource_with_mallformed_uri(self):
        """Building a resource with a malformed uri should return None"""
        wb = WorkflowBuilder()
        url = "file:test.csv"
        resource = wb.build_resource(url)
        assert resource is None

    def test_build_process(self):
        """Test building a process with shell processor"""
        wb = WorkflowBuilder()
        processor_name = "shell"
        process = wb.build_process(processor_name)
        assert process._processor.name == "shell"

    def test_build_process_with_default_processor(self):
        """Building a process with default processor should return a shell processor"""
        wb = WorkflowBuilder()
        process = wb.build_process()
        assert process._processor.name == "shell"

    def test_build_process_with_unknown_processor(self):
        """Building a process with an unknown processor should return False"""
        wb = WorkflowBuilder()
        processor_name = "unknown_processor"
        process = wb.build_process(processor_name)
        assert process is False

    def test_process_from_section(self):
        """A section extracted from the parser should build a process"""
        wb = WorkflowBuilder()
        section = {'outputs': ['file:///result1'],
                   'inputs': ['file:///source1'],
                   'processor': 'shell',
                   'process_code': "Some \nCode\n",
                   }
        resources = {}
        process = wb.process_from_section(section, resources)
        assert process._inputs[0].url == "file:///source1"
        assert process._outputs[0].url == "file:///result1"
        assert process._outputs[0].creator_process == process
        assert process._processor.name == "shell"
        assert process._code == "Some \nCode\n"

    def test_output_can_come_from_only_one_process(self):
        """A section extracted from the parser should build a process"""
        wb = WorkflowBuilder()
        section = {'outputs': ['file:///result1'],
                   'inputs': ['file:///source1'],
                   'processor': 'shell',
                   'process_code': "Some \nCode\n",
                   }
        resources = {}
        process = wb.process_from_section(section, resources)
        try:
            process = wb.process_from_section(section, resources)
            assert False
        except WorkflowError:
            assert True

    def test_resources_should_be_equals_across_processes(self):
        """Two processes using the same url should use the same resource object"""
        wb = WorkflowBuilder()
        sections = [
            {'outputs': ['file:///result1'],
             'inputs': ['file:///source1'],
             'processor': 'shell',
             'process_code': "Some \nCode\n",
             },
            {'outputs': ['file:///result2'],
             'inputs': ['file:///source1'],
             'processor': 'shell',
             'process_code': "Some \nCode\n",
             },
            ]
        resources = {}
        workflow = wb.workflow_from_project(sections)
        assert workflow.processes[0]._inputs[0] == workflow.processes[1]._inputs[0]
