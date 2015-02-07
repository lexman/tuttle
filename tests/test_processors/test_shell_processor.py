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
        sp.generate_executable(code, 12, '.')
        content = open("shell_12.bat").read()
        assert content.endswith(code)
        remove("shell_12.bat")
