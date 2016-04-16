# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE
from os.path import isfile, dirname, abspath, join

from os import path
from tests.functional_tests import isolate, run_tuttle_file


class TestPreprocessors:

    @isolate
    def test_preprocessor_is_run(self):
        """ When a preprocessoris declared, it should be run after parsing """
        project = """|<<
    echo Running preprocess
    echo preprocess_has_run > preprocess_has_run
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        # Preprocesses should not leave anything after running
        # Kids, don't do it at home !
        assert isfile('preprocess_has_run')
