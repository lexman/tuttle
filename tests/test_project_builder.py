#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nose.tools import *
from tuttle.process_builder import *

def setup():
    pass

def teardown():
    pass

def test_extract_scheme():
    "A file ressource should return a file protocol"
    pb = ProcessBuilder()
    url = "file://test.csv"
    assert pb.extract_scheme(url) == "file"

def test_cant_extract_scheme():
    "Should return False if no protocol is present"
    pb = ProcessBuilder()
    url = "LoremIpsum"
    assert pb.extract_scheme(url) == False

def test_build_file_ressource():
    "Build a file resource according to a file: uri"
    pb = ProcessBuilder()
    url = "file://test.csv"
    ressource = pb.build_ressource(url)
    assert isinstance(ressource, FileRessource)

def test_build_ressource_with_unknown_protocol():
    "Building a resource with an unknown protocol should return None"
    pb = ProcessBuilder()
    url = "unknown://test.csv"
    ressource = pb.build_ressource(url)
    assert ressource == None

def test_build_ressource_with_mallformed_uri():
    "Building a resource with a malformed uri should return None"
    pb = ProcessBuilder()
    url = "file:test.csv"
    ressource = pb.build_ressource(url)
    assert ressource == None

def test_build_process():
    "Test building a process with shell processor"
    pb = ProcessBuilder()
    processor_name = "shell"
    process = pb.build_process(processor_name)
    assert process._processor.name == "shell"

def test_build_process_with_default_processor():
    "Building a process with default processor should return a shell processor"
    pb = ProcessBuilder()
    process = pb.build_process()
    assert process._processor.name == "shell"

def test_build_process_with_unknown_processor():
    "Building a process with an unknown processor should return False"
    pb = ProcessBuilder()
    processor_name = "unknown_processor"
    process = pb.build_process(processor_name)
    assert process == False

    
def test_process_from_section():
    "A section extracted from the parser should build a process"
    pb = ProcessBuilder()
    section = { 'outputs' : ['file:///result1'],
                'inputs' : ['file:///source1'],
                'processor' : 'shell',
                'process_code' : "Some \nCode\n",
               }
    ressources = {}
    process = pb.process_from_section(section, ressources)
    assert process._inputs[0]._url == "file:///source1"
    assert process._outputs[0]._url == "file:///result1"
    assert process._processor.name == "shell"
    assert process._code == "Some \nCode\n"
    