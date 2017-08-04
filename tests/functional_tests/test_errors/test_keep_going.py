# -*- coding: utf-8 -*-

import glob
from os.path import isfile
from tests.functional_tests import isolate, run_tuttle_file
from tuttle.project_parser import ProjectParser
from tuttle.workflow_runner import WorkflowRuner


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

    @isolate(['A'])
    def test_keep_going_after_error_open(self):
        """ If a workflow fail, running it again with option keep_going,
            it should run all it can"""

        # The ordder matters
        project = """
file://C <- file://A
    echo A produces C > C
    echo A have produced C

file://D <- file://A
    echo A produces D > D
    echo A have produced D

file://E <- file://A
    echo A produces E > E
    echo A have produced E
    
file://F <- file://A
    echo A produces F > F
    echo A have produced F
    
file://G <- file://A
    echo A produces G > G
    echo A have produced G
    
file://H <- file://A
    echo A produces H > H
    echo A have produced H
    
file://B <- file://A
    echo A won't produce B > B
    echo about to fail
    error
"""
        rcode1, output1 = run_tuttle_file(project, nb_workers=1)
        assert rcode1 == 2, output1
        # Hope that tuttle has not run this process
        nb_splits = len(output1.split("A have produced"))
        # We can't control the order in which tuttle run the processes
        # but we can control the order is ok to test
        assert nb_splits < 7, \
            "Damned !  The tests won't be accurate because tuttle choose to run the failing process last \n" +\
            str(nb_splits) + "\n" + output1

        rcode, output = run_tuttle_file(project, nb_workers=1, keep_going=True)
        assert rcode == 2, output1 + "\n" + output
        assert output.find("* file://B") == -1, output

        assert output.find("A have produced") >= 0, output

    @isolate(['A'])
    def test_keep_going_after_error_no_more_process_to_run(self):
        """ If a workflow fail, running it again with option keep_going, should not run another process if
            there nothing to run
            """

        project = """file://B <- file://A
    echo A produces B > B
    echo about to fail
    error

file://C <- file://A
    sleep 1
    echo A produces C > C
    echo A have produced C

file://D <- file://B
    echo B produces D > D
    echo B have produced D
"""
        rcode1, output1 = run_tuttle_file(project, nb_workers=2)
        assert rcode1 == 2, output1

        rcode, output = run_tuttle_file(project, nb_workers=2, keep_going=True)
        assert rcode == 2, output1 + "\n" + output
        assert output.find("* file://B") == -1, output

        assert output.find("Nothing to do") >= 0, output
