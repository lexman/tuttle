#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nose.tools import *
from tuttle.project_parser import *


class TestProjectParser():

    def test_is_blank_if_empty(self):
        """Empty line should be considered blank"""
        pp = ProjectParser()
        line = "\n"
        assert pp.is_blank(line) is True

    def test_is_blank_if_blank_cars(self):
        """Line with blank characters should be blank"""
        pp = ProjectParser()
        line = "  \t \n"
        assert pp.is_blank(line) is True

    def test_is_blank_if_comment(self):
        """Line with comment should be blank"""
        pp = ProjectParser()
        line = "# un commentaire accentu�\n"
        assert pp.is_blank(line) is True

    def test_indented_line_should_not_be_blank(self):
        """Indented line should not be blank"""
        pp = ProjectParser()
        line = "\ttest"
        assert pp.is_blank(line) is False

    def test_simple_read_section(self):
        """Simple dependency line should return dependencies"""
        pp = ProjectParser()
        project = """file:///result1 <- file:///source1
        Some code
        """
        pp.set_project(project)
        pp.read_line()
        section = pp.parse_section()
        assert section['inputs'] == ['file:///source1']
        assert section['outputs'] == ['file:///result1']
        assert section['process_code'] == "Some code\n"

    def test_read_section_with_blank_line(self):
        """A blank line between dependency definition an process code should be ignored"""
        pp = ProjectParser()
        project = """file:///result1 <- file:///source1

        Some code
        """
        pp.set_project(project)
        pp.read_line()
        section = pp.parse_section()
        assert section['inputs'] == ['file:///source1']
        assert section['outputs'] == ['file:///result1']
        assert section['process_code'] == "Some code\n"

    def test_read_section_multiple_inputs_and_outputs(self):
        """Read a sections with multiple inputs and outputs"""
        pp = ProjectParser()
        project = """file:///result1,  file:///result2,  file:///result3 <- file:///source1, file:///source2
        Some code
        """
        pp.set_project(project)
        pp.read_line()
        section = pp.parse_section()
        assert section['inputs'] == ['file:///source1', 'file:///source2']
        assert section['outputs'] == ['file:///result1', 'file:///result2', 'file:///result3']
        assert section['process_code'] == "Some code\n"

    def test_read_section_without_process_code(self):
        """Read a sections without process code"""
        pp = ProjectParser()
        project = """file:///result1 <- file:///source1
        """
        pp.set_project(project)
        pp.read_line()
        section = pp.parse_section()
        print section
        assert section['inputs'] == ['file:///source1']
        assert section['outputs'] == ['file:///result1']
        assert section['process_code'] == ""

    def test_read_section_without_indentation_error_in_process_code(self):
        """Read a section with an indentation error in process code"""
        pp = ProjectParser()
        project = """file:///result1 <- file:///source1
          Some code
        More code
        """
        pp.set_project(project)
        pp.read_line()
        section = pp.parse_section()
        assert section['inputs'] == ['file:///source1']
        assert section['outputs'] == ['file:///result1']
        assert section['process_code'] == "Some code\n"

    def test_pasrse_simple_workflow(self):
        """Read a simple project"""
        pp = ProjectParser()
        project = """file:///resource1 <- file:///resource2
        Some code
        
file:///resource2 <- file:///resource3
        Some code
        More code
        """
        pp.set_project(project)
        workflow = pp.parse_project()
        assert len(workflow) == 2

    def test_pasrse_workflow_with_indentation_error(self):
        """Read a project with indentation error on first process"""
        pp = ProjectParser()
        project = """file:///resource1 <- file:///resource2
          Some code
        More code

file:///resource2 <- file:///resource3
        Some code2
        """
        pp.set_project(project)
        try:
            workflow = pp.parse_project()
        except ParsingError:
            assert True
        else:
            assert False
