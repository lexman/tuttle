# -*- coding: utf8 -*-


from nose.tools import *
from tests.functional_tests import isolate
from tuttlelib.process import Process
from tuttlelib.processors import ShellProcessor
from os import remove


class TestShellProcessor():

    @isolate
    def test_executable_generation(self):
        """Should generate an executable"""
        sp = ShellProcessor()
        code = "bla bla\nblou"
        processor = ShellProcessor()
        process = Process(processor, "tuttlefile", 12)
        process.set_code(code)
        sp.generate_executable(process, "tuttlefile_12")
        content = open("tuttlefile_12").read()
        assert content.startswith("#!")
        assert content.endswith(code)
