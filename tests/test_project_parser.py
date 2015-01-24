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
    
def test_simple_read_dependencies_and_processor():
    "Simple dependency line should return dependancies"
    pp = ProjectParser()
    project = """file:///result1 <- file:///source1\n 
    Some code
    """
    pp.set_project(project)
    section = pp.parse_section()
    assert section['inputs'] == ['file:///source1']
