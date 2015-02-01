#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nose.tools import *
from tuttle.process_builder import *


class TestProjectBuilder():

    def test_extract_scheme(self):
        """A file ressource should return a file protocol"""
        pb = ProcessBuilder()
        url = "file://test.csv"
        assert pb.extract_scheme(url) == "file"

    def test_cant_extract_scheme(self):
        """Should return False if no protocol is present"""
        pb = ProcessBuilder()
        url = "LoremIpsum"
        assert pb.extract_scheme(url) is False

    def test_build_file_ressource(self):
        """Build a file resource according to a file: uri"""
        pb = ProcessBuilder()
        url = "file://test.csv"
        ressource = pb.build_resource(url)
        assert isinstance(ressource, FileResource)

    def test_build_ressource_with_unknown_scheme(self):
        """Building a resource with an unknown protocol should return None"""
        pb = ProcessBuilder()
        url = "unknown://test.csv"
        resource = pb.build_resource(url)
        assert resource is None

    def test_build_ressource_with_mallformed_uri(self):
        """Building a resource with a malformed uri should return None"""
        pb = ProcessBuilder()
        url = "file:test.csv"
        resource = pb.build_resource(url)
        assert resource is None

    def test_build_process(self):
        """Test building a process with shell processor"""
        pb = ProcessBuilder()
        processor_name = "shell"
        process = pb.build_process(processor_name)
        assert process._processor.name == "shell"

    def test_build_process_with_default_processor(self):
        """Building a process with default processor should return a shell processor"""
        pb = ProcessBuilder()
        process = pb.build_process()
        assert process._processor.name == "shell"

    def test_build_process_with_unknown_processor(self):
        """Building a process with an unknown processor should return False"""
        pb = ProcessBuilder()
        processor_name = "unknown_processor"
        process = pb.build_process(processor_name)
        assert process is False

    def test_process_from_section(self):
        """A section extracted from the parser should build a process"""
        pb = ProcessBuilder()
        section = {'outputs': ['file:///result1'],
                   'inputs': ['file:///source1'],
                   'processor': 'shell',
                   'process_code': "Some \nCode\n",
                   }
        resources = {}
        process = pb.process_from_section(section, resources)
        assert process._inputs[0]._url == "file:///source1"
        assert process._outputs[0]._url == "file:///result1"
        assert process._outputs[0]._creator_process == process
        assert process._processor.name == "shell"
        assert process._code == "Some \nCode\n"

    def test_output_can_come_from_only_one_process(self):
        """A section extracted from the parser should build a process"""
        pb = ProcessBuilder()
        section = {'outputs': ['file:///result1'],
                   'inputs': ['file:///source1'],
                   'processor': 'shell',
                   'process_code': "Some \nCode\n",
                   }
        resources = {}
        process = pb.process_from_section(section, resources)
        try:
            process = pb.process_from_section(section, resources)
            assert False
        except WorkflowError:
            assert True

    def test_resources_should_be_equals_across_processes(self):
        """Two processes using the same url should use the same resource object"""
        pb = ProcessBuilder()
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
        workflow = pb.workflow_from_project(sections)
        assert workflow.processes[0]._inputs[0] == workflow.processes[1]._inputs[0]
