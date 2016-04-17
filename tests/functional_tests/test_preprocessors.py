# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE
from os.path import isfile, dirname, abspath, join

from os import path
from tests.functional_tests import isolate, run_tuttle_file


class TestPreprocessors:

    @isolate
    def test_preprocessor_is_run(self):
        """ When a preprocessor is declared, it should be run after parsing """
        project = """|<<
    echo Running preprocess
    echo preprocess_has_run > preprocess_has_run
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        # Preprocesses should not leave anything after running
        # Kids, don't do it at home !
        assert isfile('preprocess_has_run')

    @isolate
    def test_preprocessor_is_in_report(self):
        """ Preprocessors should appear in the report """
        project = """|<<
    echo Running preprocess
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        report_path = join('.tuttle', 'report.html')
        assert isfile(report_path)
        report = open(report_path).read()
        # the code should appear in the html report
        code_pos = report.find("echo Running preprocess")
        assert code_pos > -1, code_pos
