#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nose.tools import *
from tuttle.project_parser import *

def setup():
    print "SETUP!"

def teardown():
    print "TEAR DOWN!"

def test_is_blank_if_empty():
    "Empty line should be considereed blank"
    pp = ProjectParser()
    pp._line = "\n"
    assert pp.is_blank() == True

def test_is_blank_if_blank_cars():
    "Line with blank characters should be blank"
    pp = ProjectParser()
    pp._line = "  \t \n"
    assert pp.is_blank() == True
    
def test_is_blank_if_comment():
    "Line with comment should be blank"
    pp = ProjectParser()
    pp._line = "# un commentaire accentué\n"
    assert pp.is_blank() == True
  
def test_indented_line_should_not_be_blank():
    "Indented line should not be blank"
    pp = ProjectParser()
    pp._line = "\ttest"
    assert pp.is_blank() == False
    
def test_simple_read_section():
    "Simple dependency line should return dependancies"
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
    
def test_read_section_with_blank_line():
    "A blank line between dependency definition an process code should be ignored"
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

def test_read_section_multiple_inputs_and_outputs():
    "Read a sections with multiple inputs and outputs"
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

def test_read_section_without_process_code():
    "Read a sections with multiple inputs and outputs"
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

def test_read_section_without_indentation_error_in_process_code():
    "Read a section with indentation error in process code"
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

    
def test_pasrse_simple_workflow():
    "Read a simple project"
    pp = ProjectParser()
    project = """file:///ressource1 <- file:///ressource2
    Some code
    
file:///ressource2 <- file:///ressource3
    Some code
    More code
    """
    pp.set_project(project)
    project = pp.parse_project()
    print project
    assert False
    
def test_pasrse_workflow_with_indentation_error():
    "Read a project with identation error on first process"
    pp = ProjectParser()
    project = """file:///ressource1 <- file:///ressource2
      Some code
    More code
    
file:///ressource2 <- file:///ressource3
    Some code2
    """
    pp.set_project(project)
    project = pp.parse_project()
    print project
    assert False