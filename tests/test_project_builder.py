#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nose.tools import *
from tuttle.ProcessBuilder import *

def setup():
    pass

def teardown():
    pass

def test_extract_protocol():
    "A file ressource should return a file protocol"
    pb = ProcessBuilder()
    uri = "file://test.csv"
    assert pb.extract_protocol(uri) == "file"

def test_cant_extract_protocol():
    "Should return False if no protocol is present"
    pb = ProcessBuilder()
    uri = "LoremIpsum"
    print pb.extract_protocol(uri)
    assert pb.extract_protocol(uri) == False

def test_build_file_ressource():
    "Build a file ressource according to a file: uri"
    pb = ProcessBuilder()
    uri = "file://test.csv"
    ressource = pb.build_ressource(uri)
    assert isinstance(ressource, FileRessource)

def test_build_ressource_with_unknown_protocol():
    ""
    pb = ProcessBuilder()
    uri = "unknown://test.csv"
    ressource = pb.build_ressource(uri)
    assert ressource == None

def test_build_ressource_with_bad_uri():
    "Building a ressource with a malformed uri should return None"
    pb = ProcessBuilder()
    uri = "file:test.csv"
    ressource = pb.build_ressource(uri)
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
