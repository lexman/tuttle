#!/usr/bin/env python
# -*- coding: utf8 -*-



from nose.tools import *
from tuttle.processors import ShellProcessor
from os import remove


class TestShellProcessor():

    def test_executable_generation(self):
        """Should generate an executable"""
        sp = ShellProcessor()
        code = "bla bla\nblou"
        sp.generate_executable(code, "shell_12", '.')
        content = open("shell_12").read()
        assert content.startswith("#!")
        assert content.endswith(code)
        remove("shell_12")
