# -*- coding: utf8 -*-


from nose.tools import *
from tests.functional_tests import isolate
from tuttle.process import Process
from tuttle.processors import ShellProcessor
from os import remove


class TestShellProcessor():

    @isolate
    def test_executable_generation(self):
        """Should generate an executable"""
        sp = ShellProcessor()
        code = "bla bla\nblou"
        processor = ShellProcessor()
        process = Process(processor, 12)
        process.set_code(code)
        sp.generate_executable(process, "shell_12")
        content = open("shell_12").read()
        assert content.startswith("#!")
        assert content.endswith(code)
