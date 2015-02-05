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
        process = pp.parse_section()
        assert len(process._inputs) == 1
        assert process._inputs[0].url == 'file:///source1'
        assert len(process._outputs) == 1
        assert process._outputs[0].url == 'file:///result1'
        assert process._outputs[0].creator_process == process
        assert process._processor.name == "shell"
        assert process._code == "Some code\n"

    def test_read_section_with_blank_line(self):
        """A blank line between dependency definition an process code should be ignored"""
        pp = ProjectParser()
        project = """file:///result1 <- file:///source1

        Some code
        """
        pp.set_project(project)
        pp.read_line()
        process = pp.parse_section()
        assert len(process._inputs) == 1
        assert process._inputs[0].url == 'file:///source1'
        assert len(process._outputs) == 1
        assert process._outputs[0].url == 'file:///result1'
        assert process._code == "Some code\n"

    def test_read_section_multiple_inputs_and_outputs(self):
        """Read a sections with multiple inputs and outputs"""
        pp = ProjectParser()
        project = """file:///result1,  file:///result2,  file:///result3 <- file:///source1, file:///source2
        Some code
        """
        pp.set_project(project)
        pp.read_line()
        process = pp.parse_section()
        assert len(process._inputs) == 2
        assert process._inputs[0].url == 'file:///source1'
        assert process._inputs[1].url == 'file:///source2'
        assert len(process._outputs) == 3
        assert process._outputs[0].url == 'file:///result1'
        assert process._outputs[1].url == 'file:///result2'
        assert process._outputs[2].url == 'file:///result3'
        assert process._code == "Some code\n"

    def test_read_section_without_process_code(self):
        """Read a sections without process code"""
        pp = ProjectParser()
        project = """file:///result1 <- file:///source1
        """
        pp.set_project(project)
        pp.read_line()
        process = pp.parse_section()
        assert len(process._inputs) == 1
        assert process._inputs[0].url == 'file:///source1'
        assert len(process._outputs) == 1
        assert process._outputs[0].url == 'file:///result1'
        print process._code
        assert process._code is None

    def test_read_section_without_indentation_error_in_process_code(self):
        """Read a section with an indentation error in process code"""
        pp = ProjectParser()
        project = """file:///result1 <- file:///source1
          Some code
        More code
        """
        pp.set_project(project)
        pp.read_line()
        process = pp.parse_section()
        assert len(process._inputs) == 1
        assert process._inputs[0].url == 'file:///source1'
        assert len(process._outputs) == 1
        assert process._outputs[0].url == 'file:///result1'
        assert process._code == "Some code\n"

    def test_pasrse_simple_workflow(self):
        """Read project with a blank line with blank characters which match exactly the indentation of the code of the process"""
        pp = ProjectParser()
        project = """file:///resource1 <- file:///resource2
        Some code""" + "\n        \n" + """file:///resource2 <- file:///resource3
        Some code
        More code
        """
        pp.set_project(project)
        workflow = pp.parse_project()
        assert len(workflow.processes) == 2

    def test_pasrse_workflow_with_blank_lines(self):
        """Read project with a blank line with any number of blank characters"""
        pp = ProjectParser()
        project = """file:///resource1 <- file:///resource2
        Some code""" + "\n  \n" + """file:///resource2 <- file:///resource3
        Some code
        More code
        """
        pp.set_project(project)
        workflow = pp.parse_project()
        assert len(workflow.processes) == 2

    def test_pasrse_workflow_with_0_char_blank_lines(self):
        """Read a simple project"""
        pp = ProjectParser()
        project = """file:///resource1 <- file:///resource2
        Some code""" + "\n \n" + """file:///resource2 <- file:///resource3
        Some code
        More code
        """
        pp.set_project(project)
        workflow = pp.parse_project()
        assert len(workflow.processes) == 2

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

    def test_output_can_come_from_only_one_process(self):
        """A section extracted from the parser should build a process"""
        pp = ProjectParser()
        project = """file:///result1 <- file:///source1
        Some code

file:///result1 <- file:///source1
        other code
        """
        pp.set_project(project)
        pp.read_line()
        process = pp.parse_section()
        try:
            process = pp.parse_section()
            assert False
        except WorkflowError:
            assert True

    def test_resources_should_be_equals_across_processes(self):
        """Two processes using the same url should use the same resource object"""
        pp = ProjectParser()
        project = """file:///result1 <- file:///source1
        Some code

file:///result2 <- file:///source1
        other code
        """
        pp.set_project(project)
        workflow = pp.parse_project()
        assert workflow.processes[0]._inputs[0] == workflow.processes[1]._inputs[0]

    def test_project_should_begin_by_resources(self):
        """A project beginning by an invalid resource definition should raise an error"""
        pp = ProjectParser()
        project = """Bla
file:///result1 <- file:///source1
        Some code
        """
        pp.set_project(project)
        try:
            process = pp.parse_project()
            assert False
        except ParsingError:
            assert True

    def test_missing_inputs(self):
        """Test the list of missing inputs"""
        pp = ProjectParser()
        project = """file://result <- file://file1, file://README.txt"""
        pp.set_project(project)
        workflow = pp.parse_project()
        missing = pp.missing_inputs()
        assert len(missing) == 1
        assert missing[0].url == "file://file1"

    def test_a_project_can_have_one_line(self):
        """Test the list of missing inputs"""
        pp = ProjectParser()
        project = """file://result <- file://source"""
        pp.set_project(project)
        workflow = pp.parse_project()
        assert len(workflow.processes[0]._inputs) == 1
        assert len(workflow.processes[0]._outputs) == 1

#TODO
#Verifier qu'une ligne seule peut être acceptée : out <- in

#TODO
#    def test_section_can_have_no_inputs(self):
#        """Read project with a blank line with blank characters which match exactly the indentation of the code of the process"""
#        pp = ProjectParser()
#        section = """file:///resource1 <-
#        """
#        pp.set_project(section)
#        pp.read_line()
#        process = pp.parse_section()
#        assert len(process._inputs) == 0

#    def test_section_can_have_no_outputs(self):
#        """Read project with a blank line with blank characters which match exactly the indentation of the code of the process"""
#        pp = ProjectParser()
#        section = """ <- file:///resource
#        """
#        pp.set_project(section)
#        pp.read_line()
#        process= pp.parse_section()
#        assert len(process._outputs) == 0
