# -*- coding: utf8 -*-
from glob import glob
from tests.functional_tests import isolate
from tuttle.process import Process
from tuttle.processors import BatProcessor
from os.path import join

class TestBatProcessor():

    @isolate
    def test_executable_generation(self):
        """Should generate an executable"""
        bp = BatProcessor()
        code = "bla bla\nblou"
        processor = BatProcessor()
        process = Process(processor, "tuttlefile", 23)
        process.set_code(code)
        bp.generate_executable(process, "tuttlefile_25")
        content = open(join("tuttlefile_25", "tuttlefile_23.bat")).read()
        assert content.startswith("@echo off")
        assert content.find("bla bla") >= 0
        assert content.find("blou") >= 0
