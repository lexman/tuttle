#!/usr/bin/env python
# -*- coding: utf8 -*-



from nose.tools import *
from tuttle.processors import BatProcessor
from os import remove


class TestBatProcessor():

    def test_executable_generation(self):
        """Should generate an executable"""
        bp = BatProcessor()
        code = "bla bla\nblou"
        bp.generate_executable(code, 25, '.')
        content = open("shell_25.bat").read()
        assert content.startswith("@echo off")
        assert content.endswith(code)
        remove("shell_25.bat")
