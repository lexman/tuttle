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

    def test_cannot_build_ressource_with_only_scheme(self):
        """Building a resource with only the protocol should return None"""
        wb = WorkflowBuilder()
        url = "file://"
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
        process = wb.build_process(processor_name, "tuttlefile", 51)
        assert process._processor.name == "shell"

    def test_build_process_with_default_processor(self):
        """Building a process with default processor should return a shell processor"""
        wb = WorkflowBuilder()
        process = wb.build_process("shell", "uttlefile", 69)
        # TODO : get back to shell processors by default
        assert process._processor.name == "shell"
        assert process._line_num == 69

    def test_build_process_with_unknown_processor(self):
        """Building a process with an unknown processor should return False"""
        wb = WorkflowBuilder()
        processor_name = "unknown_processor"
        process = wb.build_process(processor_name, "tuttlefile", 69)
        assert process is False
