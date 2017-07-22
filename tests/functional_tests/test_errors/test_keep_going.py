# -*- coding: utf-8 -*-

import glob
from os.path import isfile
from tests.functional_tests import isolate, run_tuttle_file
from tuttlelib.project_parser import ProjectParser
from tuttlelib.workflow_runner import WorkflowRuner


class TestKeepGoing:

    @isolate(['A'])
    def test_keep_going(self):
        """  If tuttle is run with option keep_going, it should run all it can and not stop at first error"""
        # As in Gnu Make

        project = """file://B <- file://A
    Obvious error

file://C <- file://B
    echo B produces C > C

file://D <- file://A
    echo A produces D
    echo A produces D > D

file://E <- file://A
    Another error
"""
        rcode, output = run_tuttle_file(project, nb_workers=1, keep_going=True)
        assert rcode == 2
        assert output.find("::stderr") >= 0, output
        assert output.find("Obvious") >= 0, output
        assert output.find("Another") >= 0, output
        assert output.find("Process ended with error code 1") >= 0, output
        pos_have_failed = output.find("have failed")
        assert pos_have_failed >= 0, output
        assert output.find("tuttlefile_1", pos_have_failed) >= 0, output
        assert output.find("tuttlefile_11", pos_have_failed) >= 0, output
